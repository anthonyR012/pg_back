# Third-party Libraries
from rest_framework import serializers

# Local Modules
from services import models


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Service
        fields = (
            'id', 'name', 'description', 'confirmation_in', 'remember_in',
            'only_home_service', 'price', 'state', 'gender',
            'service_category', 'service_duration', 'images', 'amenities'
        )
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }

    price = serializers.SerializerMethodField()
    service_duration = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()

    def get_price(self, obj: models.Service):
        return obj.price

    def get_service_duration(self, obj: models.Service):
        import random
        return random.randint(15, 60)

    def get_images(self, obj: models.Service):
        host = self.context.get('request').build_absolute_uri('/')
        return obj.get_url_images(host)

    def get_amenities(self, obj: models.Service):
        return obj.get_amenities()


class ServiceFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ServiceFile
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }


class ServiceCategorySerializer(serializers.ModelSerializer):

    picture = serializers.SerializerMethodField()

    class Meta:
        model = models.ServiceCategory
        fields = '__all__'

    # TODO: Agregar validacion de URL
    def get_picture(self, obj):
        import re
        request = self.context.get('request')

        if obj.picture:
            picture_url = obj.picture.url
            print(picture_url)
            # Verificar si la URL comienza con http o https
            if not re.match(r'^https?://', picture_url):
                print(request.get_host())
                # Si no comienza con http o https, agregar la URL del servidor
                picture_url = 'http://' + request.get_host() + picture_url

            print(picture_url)
            return picture_url
        return None


class SimpleAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SimpleAppointment
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }
