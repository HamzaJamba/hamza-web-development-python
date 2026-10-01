from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count


class Review(models.Model):
    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["product", "user"], name="one_review_per_user_per_product")]

    def __str__(self):
        return f"{self.product_id} {self.rating}"

    def _refresh_product(self):
        agg = Review.objects.filter(product_id=self.product_id).aggregate(avg=Avg("rating"), n=Count("id"))
        from catalog.models import Product
        Product.objects.filter(pk=self.product_id).update(
            rating_avg=round(agg["avg"] or 0, 2), rating_count=agg["n"] or 0
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._refresh_product()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self._refresh_product()
