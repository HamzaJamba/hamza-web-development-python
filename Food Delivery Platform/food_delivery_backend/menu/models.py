import uuid
from django.conf import settings
from django.db import models
from restaurants.models import Restaurant


class Category(models.Model):
    """Global categories managed by Admin (Pizza, Burger, Biryani...)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    icon = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class FoodItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="food_items")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="food_items")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0, help_text="Denormalized counter for 'Best Selling Food'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["restaurant", "is_available"])]

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


class FoodImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="food_items/")
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.food_item.name}"


class WishlistItem(models.Model):
    """Customer's saved favourite food items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items"
    )
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "food_item")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.customer.username} \u2665 {self.food_item.name}"
