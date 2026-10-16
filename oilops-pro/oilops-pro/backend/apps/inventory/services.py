from decimal import Decimal

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import Role
from apps.notifications.services import notify, users_with_roles

from .models import Item, StockMovement


@transaction.atomic
def adjust_stock(item_id, movement_type, quantity, user=None, reference="", notes=""):
    """Row-locked stock change. IN adds, OUT subtracts, ADJUST sets the absolute level."""
    quantity = Decimal(quantity)
    if quantity < 0 or (movement_type != StockMovement.Type.ADJUST and quantity == 0):
        raise ValidationError({"quantity": "Quantity must be positive."})
    item = Item.objects.select_for_update().get(pk=item_id)
    was_low = item.is_low
    if movement_type == StockMovement.Type.IN:
        item.quantity += quantity
    elif movement_type == StockMovement.Type.OUT:
        if item.quantity < quantity:
            raise ValidationError({"quantity": f"Insufficient stock for {item.sku}: {item.quantity} {item.unit} available."})
        item.quantity -= quantity
    elif movement_type == StockMovement.Type.ADJUST:
        item.quantity = quantity
    else:
        raise ValidationError({"movement_type": "Invalid movement type."})
    item.save(update_fields=["quantity", "updated_at"])
    movement = StockMovement.objects.create(
        item=item, movement_type=movement_type, quantity=quantity, balance_after=item.quantity,
        reference=reference, notes=notes, performed_by=user if getattr(user, "pk", None) else None)
    if item.is_low and not was_low:
        notify_low_stock(item)
    return movement


def notify_low_stock(item):
    notify(users_with_roles(Role.STORE_KEEPER, Role.PLANT_MANAGER), "LOW_STOCK",
           f"Low stock: {item.name}",
           f"{item.sku} is at {item.quantity} {item.unit} (reorder level {item.reorder_level}).",
           "/inventory", severity="warning", email=True)
