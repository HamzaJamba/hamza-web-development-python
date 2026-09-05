from django.conf import settings
from django.db import models
from common.models import TimeStampedModel


class TourPackage(TimeStampedModel):
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tour_packages')
    name = models.CharField(max_length=200)
    destination = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    days = models.PositiveIntegerField()
    nights = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    included_services = models.JSONField(default=list, blank=True)
    excluded_services = models.JSONField(default=list, blank=True)
    cover_image = models.ImageField(upload_to='tours/covers/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TourImage(TimeStampedModel):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tours/gallery/')


class TourSchedule(TimeStampedModel):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='schedule')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['day_number']
