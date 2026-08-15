from django.db.models import Avg, Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review


@receiver(post_save, sender=Review)
def update_avg_ratings(sender, instance, created, **kwargs):
    if not created:
        return

    restaurant = instance.restaurant
    agg = Review.objects.filter(restaurant=restaurant).aggregate(avg=Avg("rating"), count=Count("id"))
    restaurant.avg_rating = round(agg["avg"] or 0, 2)
    restaurant.total_reviews = agg["count"]
    restaurant.save(update_fields=["avg_rating", "total_reviews"])

    if instance.food_item_id:
        food_item = instance.food_item
        agg = Review.objects.filter(food_item=food_item).aggregate(avg=Avg("rating"), count=Count("id"))
        food_item.avg_rating = round(agg["avg"] or 0, 2)
        food_item.total_reviews = agg["count"]
        food_item.save(update_fields=["avg_rating", "total_reviews"])
