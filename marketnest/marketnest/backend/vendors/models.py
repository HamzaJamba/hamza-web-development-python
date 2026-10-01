from django.conf import settings
from django.db import models
from django.utils.text import slugify
import uuid


class Vendor(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendor")
    shop_name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    tagline = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    # The awning colours identify the stall everywhere in the UI.
    awning_primary = models.CharField(max_length=7, default="#2C3BE6")
    awning_secondary = models.CharField(max_length=7, default="#FFFFFF")
    commission_rate = models.DecimalField(max_digits=4, decimal_places=2, default=10)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["shop_name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.shop_name) or "stall"
            slug = base
            while Vendor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{uuid.uuid4().hex[:4]}"
            self.slug = slug
        super().save(*args, **kwargs)
        if self.is_approved:
            from roles.models import Role
            owner = self.owner
            if owner.role_id is None or owner.role.name == Role.CUSTOMER:
                owner.role = Role.get(Role.VENDOR)
                owner.save(update_fields=["role"])

    def __str__(self):
        return self.shop_name
