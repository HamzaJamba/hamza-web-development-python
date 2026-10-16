from django.contrib import admin

from .models import Pipeline, Plant, StorageTank

admin.site.register(Plant)
admin.site.register(Pipeline)
admin.site.register(StorageTank)
