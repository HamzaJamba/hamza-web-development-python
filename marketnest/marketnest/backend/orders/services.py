from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from rest_framework.exceptions import ValidationError
from catalog.models import Product
from payments.gateway import charge
from payments.models import Payment
from django.utils import timezone
from .models import Order, OrderItem

FREE_SHIPPING_FROM = Decimal("5000")
SHIPPING_FEE = Decimal("250")


class PaymentDeclined(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def money(v):
    return Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@transaction.atomic
def create_order(user, data):
    """Create an order from a cart payload. Prices always come from the database, never the client."""
    # merge duplicate lines
    wanted = {}
    for line in data["items"]:
        p = line["product"]
        wanted[p.pk] = wanted.get(p.pk, 0) + line["quantity"]

    products = {p.pk: p for p in Product.objects.select_for_update().select_related("vendor").filter(pk__in=wanted)}
    subtotal = Decimal("0")
    lines = []
    for pk, qty in wanted.items():
        product = products[pk]
        if not product.is_active or not product.vendor.is_approved:
            raise ValidationError({"items": f"{product.name} is no longer available."})
        if product.stock < qty:
            left = "sold out" if product.stock == 0 else f"only {product.stock} left"
            raise ValidationError({"items": f"{product.name}: {left}."})
        line_total = money(product.price * qty)
        subtotal += line_total
        lines.append((product, qty, line_total))

    shipping = Decimal("0") if subtotal >= FREE_SHIPPING_FROM else SHIPPING_FEE
    total = subtotal + shipping

    order = Order.objects.create(
        customer=user, payment_method=data["payment_method"], subtotal=subtotal,
        shipping_fee=shipping, total=total, full_name=data["full_name"], phone=data["phone"],
        address=data["address"], city=data["city"],
    )

    for product, qty, line_total in lines:
        commission = money(line_total * product.vendor.commission_rate / 100)
        OrderItem.objects.create(
            order=order, product=product, vendor=product.vendor, product_name=product.name,
            unit_price=product.price, quantity=qty, line_total=line_total, commission=commission,
        )
        product.stock -= qty
        product.sold_count += qty
        product.save(update_fields=["stock", "sold_count", "updated_at"])

    payment = Payment(order=order, method=data["payment_method"], amount=total)
    if data["payment_method"] == Payment.CARD:
        result = charge(data.get("card_number", ""), total)
        if not result.success:
            raise PaymentDeclined(result.message)  # rolls the whole transaction back
        payment.status = Payment.PAID
        payment.reference = result.reference
        payment.card_last4 = result.last4
        payment.paid_at = timezone.now()
        order.payment_status = "paid"
        order.save(update_fields=["payment_status"])
    payment.save()
    return order


@transaction.atomic
def restock_item(item):
    if item.product_id:
        p = Product.objects.select_for_update().get(pk=item.product_id)
        p.stock += item.quantity
        p.sold_count = max(0, p.sold_count - item.quantity)
        p.save(update_fields=["stock", "sold_count", "updated_at"])
