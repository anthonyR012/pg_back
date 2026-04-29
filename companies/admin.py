# Third-party Libraries
from django.contrib import admin

# Local Modules
from companies import models


# Register your models here.
admin.site.register(models.Company)
admin.site.register(models.Headquarter)
admin.site.register(models.HeadquarterService)
admin.site.register(models.HeadquarterWorker)
admin.site.register(models.HeadquaterWeekDayTimeConfiguration)
admin.site.register(models.CompanyFile)
admin.site.register(models.HeadquarterFile)
admin.site.register(models.HeadquarterRating)
admin.site.register(models.HeadquarterLike)
