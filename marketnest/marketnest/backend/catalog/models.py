import uuid
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=40, default="Package", help_text="lucide-react icon name")
    hue = models.PositiveSmallIntegerField(default=220)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    vendor = models.ForeignKey("vendors.Vendor", on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    hue = models.PositiveSmallIntegerField(default=200, help_text="Colour of the generated product plate")
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["is_active", "-created_at"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{slugify(self.name)[:150]}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
