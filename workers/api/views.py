# Third-party Libraries
# from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from datetime import datetime, timedelta, time
# Local Modules
from workers import models
from workers.api import serializers
# from core import utils

from companies.models import HeadquarterWorker
from users.models import User
from services.models import WorkerService, AppointmentService, Service


class CreateWorker(viewsets.ModelViewSet):
    serializer_class = serializers.WorkerSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        data['created_by_user_id'] = request.user.pk

        worker = models.Worker.objects.filter(
            user_id=data['user']
        ).first()

        serializer = self.serializer_class(instance=worker, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        worker_hq, _ = HeadquarterWorker.objects.get_or_create(
            worker=serializer.instance,
            headquarter_id=data['head_quarter'],
            defaults={
                'created_by_user_id': request.user.pk
            }
        )

        worker_hq.save()

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )


class ListWorkers(viewsets.ModelViewSet):

    queryset = models.Worker.objects.all().order_by('-created_at')
    serializer_class = serializers.WorkerUserSerializer
    authentication_classes = [TokenAuthentication]

    def list(self, request: Request, *args, **kwargs):
        head_quarter_id = request.GET.get('head_quarter_id')
        service_id = request.GET.get('service_id')

        queryset = self.filter_queryset(self.get_queryset())

        if head_quarter_id:
            queryset = queryset.filter(
                headquarter_worker__headquarter_id=head_quarter_id
            )

        if service_id:
            queryset = queryset.filter(
                worker_service__service_id=service_id
            )

        users = User.objects.filter(
            pk__in=list(queryset.values_list('user', flat=True))
        )
        serializer = self.get_serializer(users, many=True)
        return Response(
            {
                'success': serializer.data
            }
        )


class ListAvailableSlots(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]

    def list(self, request, *args, **kwargs):
        service_id = request.GET.get('service_id')
        # head_quarter_id = request.GET.get('head_quarter_id')
        date_str = request.GET.get('date')  # formato 'YYYY-MM-DD'
        worker_id = request.GET.get('worker_id')

        if not service_id or not date_str:
            return Response({'error': 'service_id y date son requeridos'},
                            status=400)

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        service = Service.objects.get(pk=service_id)

        # obtener duración del servicio
        try:
            time_conf = service.time_configuration_service.first()
            duration = timedelta(
                hours=time_conf.time_configuration.hours,
                minutes=time_conf.time_configuration.minutes
            )
        except Exception:
            return Response({'error': 'Duración del servicio no configurada'},
                            status=400)

        # obtener trabajadores disponibles
        worker_qs = WorkerService.objects.filter(service=service)
        if worker_id:
            worker_qs = worker_qs.filter(worker_id=worker_id)

        results = []

        for worker_service in worker_qs:
            worker = worker_service.worker

            # Define horario fijo (8am-5pm) para ejemplo simple
            current_time = datetime.combine(date, time(8, 0))
            end_of_day = datetime.combine(date, time(17, 0))

            while current_time + duration <= end_of_day:
                if self.is_slot_available(worker, current_time, duration):
                    results.append({
                        'worker_id': worker.id,
                        'worker_name': str(worker),
                        'start_time': current_time,
                        'end_time': current_time + duration
                    })
                current_time += timedelta(minutes=30)  # paso de media hora

        serializer = serializers.AvailableSlotSerializer(results, many=True)
        return Response({'success': serializer.data})

    def is_slot_available(self, worker, start_time, duration):
        end_time = start_time + duration
        overlapping = AppointmentService.objects.filter(
            worker=worker,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        return not overlapping.exists()
