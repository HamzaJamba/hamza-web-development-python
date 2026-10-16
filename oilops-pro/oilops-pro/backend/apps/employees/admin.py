from django.contrib import admin

from . import models

for m in (models.Department, models.Position, models.Shift, models.SalaryGrade, models.Employee,
          models.TrainingRecord, models.Certification):
    admin.site.register(m)
