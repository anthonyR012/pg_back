# Third-party Libraries
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Local Modules
from core.models import MixinAudit, FileMixin
from core import constants


# Create your models here.
class Company(MixinAudit):

    name = models.TextField()
    description = models.TextField()
    type = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='type_company'
    )
    state = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='state_company'
    )

    def __str__(self):
        return self.name

    def get_users_liked(self):
        return HeadquarterLike.objects.filter(
            headquarter__company=self).values_list('user_id', flat=True)


class Headquarter(MixinAudit):

    name = models.TextField()
    phone_number = models.TextField()
    address = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    rating_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    geo_reference_city = models.ForeignKey(
        'core.GeoReferenceCity', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    type = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='type_headquarter'
    )
    state = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='state_headquarter'
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter'
    )
    country = models.ForeignKey(
        'cities_light.Country', on_delete=models.SET_NULL, null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def get_company_picture_url(self, host):

        image = CompanyFile.objects.filter(
            company=self.company,
            type__code=constants.PROFILE_IMAGE
        ).first()

        if image:
            return f'{host}media/{image.file}'

        return None


class HeadquarterService(MixinAudit):

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE,
        related_name='headquarter_service'
    )
    service = models.ForeignKey(
        'services.Service', on_delete=models.CASCADE,
        related_name='headquarter_service'
    )
    rating_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0)

    def __str__(self) -> str:
        return f'Hq: {self.headquarter} - Service: {self.service}'


class HeadquarterWorker(MixinAudit):

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_worker'
    )
    worker = models.ForeignKey(
        'workers.Worker', on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_worker'
    )


class HeadquaterWeekDayTimeConfiguration(MixinAudit):

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquater_week_day_time_configuration'
    )
    week_day_time_configuration = models.ForeignKey(
        'core.WeekDayTimeConfiguration', on_delete=models.CASCADE,
        null=True, blank=True
    )


class CompanyFile(FileMixin):

    @staticmethod
    def generate_file_name(instance, filename):
        path = 'companies/{0}/{1}'.format(
            instance.company.name,
            filename
        )
        return path

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True,
        related_name='company_file'
    )

    def __str__(self):
        return self.file.name


class HeadquarterFile(FileMixin):

    @staticmethod
    def generate_file_name(instance, filename):
        path = 'companies/{0}/{1}/{2}'.format(
            instance.headquarter.company.name,
            instance.headquarter.name,
            filename
        )
        return path

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_file'
    )

    def __str__(self):
        return self.file.name


class HeadquarterRating(MixinAudit):

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_rating'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_rating'
    )
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )

    def __str__(self):
        return self.comment


class HeadquarterServiceRating(MixinAudit):

    headquarter_service = models.ForeignKey(
        HeadquarterService, on_delete=models.CASCADE,
        related_name='headquarter_service_rating'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_service_rating'
    )
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ]
    )
    comment = models.TextField()

    def __str__(self):
        return self.comment


class HeadquarterLike(MixinAudit):

    headquarter = models.ForeignKey(
        Headquarter, on_delete=models.CASCADE, null=True, blank=True,
        related_name='headquarter_like'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, blank=True,
    )

    def __str__(self):
        return f'{self.headquarter} - {self.user}'
