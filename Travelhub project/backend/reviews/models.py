from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from hotels.models import Hotel
from tours.models import TourPackage


class Review(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.hotel or self.tour_package
        return f'{self.user.username} -> {target} ({self.rating}★)'
