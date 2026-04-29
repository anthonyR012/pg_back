# third-party Libraries
from rest_framework import serializers

# Local Modules
from workers import models
from users.api.serializers import BaseUserSerializer


class WorkerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Worker
        fields = '__all__'
        extra_kwargs = {
            'file': {'required': False},
            'status': {'required': False},
            'type': {'required': False}
        }


class WorkerUserSerializer(BaseUserSerializer):
    worker_id = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = '__all__'  # Hereda todos los campos de BaseUserSerializer

    def get_worker_id(self, obj):
        worker = models.Worker.objects.filter(user=obj).first()
        return worker.pk if worker else None


class AvailableSlotSerializer(serializers.Serializer):
    worker_id = serializers.IntegerField()
    worker_name = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
