# Third-party Libraries
from django.db import models
# from datetime import datetime

# Local Modules
from core.models import MixinAudit


# Create your models here.
class Worker(MixinAudit):

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='worker')
    status = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='status_worker'
    )
    type = models.ForeignKey(
        'core.Type', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='type_worker'
    )

    def __str__(self):
        return str(self.user)


class WorkerAvailability(models.Model):
    worker = models.ForeignKey('workers.Worker', on_delete=models.CASCADE)
    weekday = models.IntegerField()  # 0=Lunes, ..., 6=Domingo
    start_time = models.TimeField()
    end_time = models.TimeField()


class WorkerLevel(MixinAudit):

    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name='worker_level'
    )
    level = models.ForeignKey(
        'core.Level', on_delete=models.CASCADE,
        related_name='worker_level'
    )

    def __str__(self):
        return self.worker
