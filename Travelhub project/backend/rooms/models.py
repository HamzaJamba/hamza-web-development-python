from django.db import models
from common.models import TimeStampedModel
from hotels.models import Hotel


class Room(TimeStampedModel):
    class BedType(models.TextChoices):
        SINGLE = 'single', 'Single'
        DOUBLE = 'double', 'Double'
        QUEEN = 'queen', 'Queen'
        KING = 'king', 'King'

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    bed_type = models.CharField(max_length=20, choices=BedType.choices, default=BedType.DOUBLE)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.PositiveIntegerField(default=2)
    has_wifi = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.hotel.name}'


class RoomImage(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/gallery/')


class RoomAvailability(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    is_blocked = models.BooleanField(default=False)  # manually blocked by owner

    class Meta:
        unique_together = ['room', 'date']
