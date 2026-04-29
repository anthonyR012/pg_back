# Python Standard Library
from datetime import datetime

# Third-party Libraries
from django.db import models
from services.managers import ServiceManager

# Local Modules
from core.models import MixinAudit


# Create your models here.
class Service(MixinAudit):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    confirmation_in = models.IntegerField()
    remember_in = models.IntegerField()
    only_home_service = models.BooleanField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='state_service'
    )
    gender = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='gender_service'
    )
    service_category = models.ForeignKey(
        'ServiceCategory', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='service_category'
    )

    objects = ServiceManager()

    def __str__(self) -> str:
        return self.name

    def get_url_images(self, host):
        images = list(
            self.service_file.all().values_list(
                'file', flat=True
            )
        )
        url_images = map(lambda x: f'{host}media/{x}', images)
        return list(url_images)

    def get_amenities(self):
        amenities = ServiceAmenity.objects.filter(
            service=self
        ).values_list('amenity', flat=True)
        return amenities


class ServiceFile(MixinAudit):

    def generate_file_name(instance, filename):
        date = datetime.now()
        return f'services/{date.year}/{date.month}/{date.day}/' +\
               f'{instance.service.pk}/{filename}'

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, blank=True,
        related_name='service_file'
    )
    file = models.FileField(
        upload_to=generate_file_name, null=True, blank=True
    )
    type = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='type_service_file'
    )


class ServiceCategory(MixinAudit):

    def generate_file_name(instance, filename):
        return f'service_category/{filename}'

    description = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    picture = models.FileField(
        upload_to=generate_file_name, null=True, blank=True
    )
    state = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='state_service_category'
    )

    def __str__(self):
        return self.description


class Appointment(MixinAudit):

    confirmation_in = models.DateTimeField()
    remember_in = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='state_appointment'
    )
    type = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='type_appointment'
    )


class AppointmentService(MixinAudit):

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE,
        related_name='appointment_service'
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='appointment_service'
    )
    worker = models.ForeignKey(
        'workers.Worker', on_delete=models.CASCADE,
        related_name='appointment_service'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class TimeConfigurationService(MixinAudit):

    time_configuration = models.ForeignKey(
        'core.TimeConfiguration', on_delete=models.CASCADE,
        related_name='time_configuration_service'
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE,
        related_name='time_configuration_service'
    )


class WorkerService(MixinAudit):

    worker = models.ForeignKey(
        'workers.Worker', on_delete=models.CASCADE,
        related_name='worker_service'
    )
    service = models.ForeignKey(
        'services.Service', on_delete=models.CASCADE,
        related_name='worker_service'
    )

    def __str__(self):
        return str(self.worker)


class ServiceAmenity(MixinAudit):

    amenity = models.ForeignKey(
        'core.Amenity', on_delete=models.CASCADE,
        related_name='service_amenity'
    )
    service = models.ForeignKey(
        'services.Service', on_delete=models.CASCADE,
        related_name='service_amenity'
    )


class Slot(MixinAudit):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_reserved = models.BooleanField(default=False)
