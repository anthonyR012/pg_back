# Third-party Libraries
from rest_framework import serializers

# Local Modules
from companies import models
from services.api.serializers import ServiceSerializer
from services.models import Service


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Company
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }


class CompanyFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyFile
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }


class HeadquarterSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Headquarter
        fields = [f.name for f in models.Headquarter._meta.fields]\
            + ['image_url']
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }

    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj: models.Headquarter):
        return obj.get_company_picture_url()


class HeadquarterWithServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Headquarter
        fields = [
            'id', 'created_at', 'updated_at', 'created_by_user_id',
            'modified_by_user_id', 'name', 'phone_number', 'address',
            'latitude', 'longitude', 'rating_count', 'rating', 'like',
            'geo_reference_city', 'type', 'company', 'name_company',
            'country', 'image_url', 'services'
        ]
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }

    like = serializers.SerializerMethodField()
    name_company = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    def get_like(self, obj: models.Headquarter):
        return obj.headquarter_like.filter(
            user_id=self.context.get('request').user.id
        ).exists()

    def get_name_company(self, obj: models.Headquarter):
        return obj.company.name

    def get_image_url(self, obj: models.Headquarter):
        host = self.context.get('request').build_absolute_uri('/')
        return obj.get_company_picture_url(host)

    def get_services(self, obj: models.Headquarter):
        request = self.context.get('request')
        category = self.context.get('category')
        additional_filters = self.context.get('additional_filters')

        services = obj.headquarter_service.values_list('service', flat=True)

        filters = {
            'id__in': services
        }

        filters.update(additional_filters)

        if category:
            filters['service_category__pk'] = category

        serialized_services = ServiceSerializer(
            Service.objects.filter(
                **filters
            ).distinct(),
            many=True,
            context={'request': request}
        ).data
        return serialized_services


class HeadquarterFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.HeadquarterFile
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }


class HeadquarterRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.HeadquarterRating
        fields = '__all__'
        extra_kwargs = {
            'created_by_user_id': {'required': True},
        }
