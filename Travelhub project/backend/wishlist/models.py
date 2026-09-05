from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from hotels.models import Hotel
from tours.models import TourPackage


class WishlistItem(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    tour_package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = [('user', 'hotel'), ('user', 'tour_package')]

    def __str__(self):
        return f'{self.user.username} wishlist -> {self.hotel or self.tour_package}'
