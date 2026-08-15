from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import Address
from cart.models import Cart
from dashboard.models import PlatformSettings
from orders.models import Order, OrderItem, Coupon
from notifications.models import Notification
from riders.models import Delivery


def _apply_coupon(code, subtotal):
    if not code:
        return None, Decimal("0.00")
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        raise ValidationError({"coupon_code": "Invalid or inactive coupon."})

    now = timezone.now()
    if not (coupon.valid_from <= now <= coupon.valid_until):
        raise ValidationError({"coupon_code": "Coupon is not valid right now."})
    if coupon.times_used >= coupon.usage_limit:
        raise ValidationError({"coupon_code": "Coupon usage limit reached."})
    if subtotal < coupon.min_order_amount:
        raise ValidationError({"coupon_code": f"Minimum order amount is {coupon.min_order_amount}."})

    if coupon.discount_type == Coupon.DiscountType.PERCENT:
        discount = subtotal * (coupon.discount_value / Decimal("100"))
        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)
    else:
        discount = coupon.discount_value

    return coupon, min(discount, subtotal)


@transaction.atomic
def checkout(customer, delivery_address_id, payment_method, coupon_code=None):
    try:
        cart = Cart.objects.select_related("restaurant").prefetch_related("items__food_item").get(customer=customer)
    except Cart.DoesNotExist:
        raise ValidationError("Your cart is empty.")

    if not cart.restaurant_id or not cart.items.exists():
        raise ValidationError("Your cart is empty.")

    try:
        address = Address.objects.get(id=delivery_address_id, user=customer)
    except Address.DoesNotExist:
        raise ValidationError({"delivery_address_id": "Address not found."})

    if not cart.restaurant.is_open or cart.restaurant.status != "APPROVED":
        raise ValidationError("This restaurant is not currently accepting orders.")

    platform_settings = PlatformSettings.load()
    delivery_charge = Decimal(str(platform_settings.delivery_charge))
    tax_rate = Decimal(str(platform_settings.tax_rate_percent)) / Decimal("100")

    subtotal = cart.subtotal
    coupon, discount_amount = _apply_coupon(coupon_code, subtotal)
    tax = (subtotal * tax_rate).quantize(Decimal("0.01"))
    grand_total = subtotal + delivery_charge + tax - discount_amount

    commission_rate = Decimal(str(platform_settings.platform_commission_percent))
    commission_amount = (subtotal * commission_rate / Decimal("100")).quantize(Decimal("0.01"))
    restaurant_payout = subtotal - commission_amount

    order = Order.objects.create(
        customer=customer,
        restaurant=cart.restaurant,
        delivery_address=address,
        coupon=coupon,
        subtotal=subtotal,
        delivery_charges=delivery_charge,
        tax=tax,
        discount_amount=discount_amount,
        grand_total=grand_total,
        platform_commission_percent_snapshot=commission_rate,
        platform_commission_amount=commission_amount,
        restaurant_payout=restaurant_payout,
    )

    for cart_item in cart.items.all():
        food = cart_item.food_item
        OrderItem.objects.create(
            order=order,
            food_item=food,
            food_name_snapshot=food.name,
            unit_price_snapshot=food.discount_price or food.price,
            quantity=cart_item.quantity,
            special_instructions=cart_item.special_instructions,
        )
        food.total_orders += cart_item.quantity
        food.save(update_fields=["total_orders"])

    if coupon:
        coupon.times_used += 1
        coupon.save(update_fields=["times_used"])

    cart.items.all().delete()
    cart.restaurant = None
    cart.save(update_fields=["restaurant"])

    Notification.objects.create(
        recipient=customer,
        type=Notification.Type.ORDER_PLACED,
        title="Order placed",
        message=f"Your order {order.order_number} has been placed.",
        related_order_id=order.id,
    )
    Notification.objects.create(
        recipient=order.restaurant.owner,
        type=Notification.Type.ORDER_PLACED,
        title="New order received",
        message=f"New order {order.order_number} needs your confirmation.",
        related_order_id=order.id,
    )

    return order, payment_method


VALID_TRANSITIONS = {
    Order.Status.PENDING: {Order.Status.ACCEPTED, Order.Status.CANCELLED},
    Order.Status.ACCEPTED: {Order.Status.PREPARING, Order.Status.CANCELLED},
    Order.Status.PREPARING: {Order.Status.READY_FOR_PICKUP, Order.Status.CANCELLED},
    Order.Status.READY_FOR_PICKUP: {Order.Status.OUT_FOR_DELIVERY},
    Order.Status.OUT_FOR_DELIVERY: {Order.Status.COMPLETED},
}

STATUS_NOTIFICATION_MAP = {
    Order.Status.ACCEPTED: Notification.Type.ORDER_ACCEPTED,
    Order.Status.PREPARING: Notification.Type.FOOD_PREPARING,
    Order.Status.OUT_FOR_DELIVERY: Notification.Type.RIDER_ASSIGNED,
    Order.Status.COMPLETED: Notification.Type.DELIVERED,
    Order.Status.CANCELLED: Notification.Type.ORDER_CANCELLED,
}


@transaction.atomic
def transition_status(order, new_status, actor):
    allowed = VALID_TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        raise ValidationError(f"Cannot move order from {order.status} to {new_status}.")

    order.status = new_status
    if new_status == Order.Status.ACCEPTED:
        order.accepted_at = timezone.now()
    elif new_status == Order.Status.COMPLETED:
        order.completed_at = timezone.now()
    elif new_status == Order.Status.CANCELLED:
        order.cancelled_at = timezone.now()
    order.save()

    if new_status == Order.Status.READY_FOR_PICKUP:
        # Order is ready — open it up as an available delivery for riders to accept.
        Delivery.objects.get_or_create(order=order)

    notif_type = STATUS_NOTIFICATION_MAP.get(new_status)
    if notif_type:
        Notification.objects.create(
            recipient=order.customer,
            type=notif_type,
            title=notif_type.replace("_", " ").title(),
            message=f"Order {order.order_number} is now {order.get_status_display()}.",
            related_order_id=order.id,
        )
    return order
