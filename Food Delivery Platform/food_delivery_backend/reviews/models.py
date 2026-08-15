import uuid
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from menu.models import FoodItem
from orders.models import Order
from restaurants.models import Restaurant


class Review(models.Model):
    """A single review tied to one order — covers restaurant rating and/or a food item rating."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reviews")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")
    food_item = models.ForeignKey(
        FoodItem, on_delete=models.CASCADE, null=True, blank=True, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_flagged = models.BooleanField(default=False, help_text="Set by moderation")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "order", "food_item")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}★ by {self.customer.username}"


class ReviewImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="reviews/")
