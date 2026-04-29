# Python Standard Library
from django.contrib import admin

# Local Modules
from core import models


# Register your models here.
admin.site.register(models.Category)
admin.site.register(models.Type)
admin.site.register(models.WeekDay)
admin.site.register(models.TimeConfiguration)
admin.site.register(models.WeekDayTimeConfiguration)
admin.site.register(models.HourWeekDayTimeConfiguration)
admin.site.register(models.Level)
admin.site.register(models.Amenity)
admin.site.register(models.GeoReferenceCity)
admin.site.register(models.MobileAppLog)
