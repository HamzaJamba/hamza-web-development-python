from decimal import Decimal
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from roles.models import Role
from vendors.models import Vendor

User = get_user_model()


def make_user(email, role=Role.CUSTOMER, **kw):
    return User.objects.create_user(email=email, password="StrongPass123", role=Role.get(role), **kw)


def make_vendor(email="stall@test.pk", shop="Test Stall", approved=True, commission=10):
    owner = make_user(email, Role.VENDOR if approved else Role.CUSTOMER)
    return Vendor.objects.create(owner=owner, shop_name=shop, is_approved=approved, commission_rate=commission)


def make_category(slug="fashion", name="Fashion"):
    return Category.objects.get_or_create(slug=slug, defaults={"name": name})[0]


def make_product(vendor, name="Kurta", price="1000", stock=10, category=None, **kw):
    return Product.objects.create(
        vendor=vendor, category=category or make_category(), name=name,
        price=Decimal(price), stock=stock, **kw)


CHECKOUT = {
    "full_name": "Ayesha Khan", "phone": "03001234567",
    "address": "12 Canal Road", "city": "Lahore", "payment_method": "cod",
}
