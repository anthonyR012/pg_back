"""
File for the API views of the companies application
"""

# Third-party Libraries
# from django.core.cache import cache
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.authentication import (
    BasicAuthentication, TokenAuthentication
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

# Local Modules
from companies.api.serializers import HeadquarterWithServicesSerializer
from companies.models import Headquarter, HeadquarterService
from core import models as core_models
from core import utils
from services import models
from services.api import serializers


class CreateService(viewsets.ViewSet):

    serializer_class_service = serializers.ServiceSerializer
    serializer_class_file_service = serializers.ServiceFileSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):

        data = request.data.copy()
        headquarter_id = data.get('headquarter_id')
        created_by_user_id = request.user.pk
        data['created_by_user_id'] = created_by_user_id

        service = self.get_or_create_service(data)
        self.get_or_create_files(data)
        # self.get_or_create_service_amenities(data, service)
        self.get_or_create_headquarter_service(service, headquarter_id)

        return Response(
            {
                'service_id': service.id
            },
            status=status.HTTP_200_OK
        )

    def get_or_create_service(self, data):
        # test
        service_name = data.get('name')
        created_by_user_id = data.get('created_by_user_id')

        service = models.Service.objects.filter(
            name=service_name, created_by_user_id=created_by_user_id
        ).first()

        if not service:
            serializer_service = self.serializer_class_service(data=data)
            serializer_service.is_valid(raise_exception=True)
            service = serializer_service.save()
            self.status_class = status.HTTP_201_CREATED

        data['service'] = service.id
        return service

    def get_or_create_files(self, data: Request):

        type_file_service_image = \
            core_models.Type.objects.get_type(
                code='service_image',
                category_type_code='type_file'
            )

        data_file_service = []

        service_id = data.get('service_id')
        additional_service_image = data.getlist('service_image')
        created_by_user_id = data.get('created_by_user_id')

        for image in additional_service_image:

            data_file_service.append(
                {
                    'service_id': service_id,
                    'type_id': type_file_service_image.id,
                    'file': image,
                    'created_by_user_id': created_by_user_id
                }
            )

        if data_file_service:
            serializer_file_service = self.serializer_class_file_service(
                data=data_file_service, many=True
            )
            serializer_file_service.is_valid(raise_exception=True)
            serializer_file_service.save()

    def get_or_create_service_amenities(self, data, service):

        amenities = data.get('amenities')

        for amenity in amenities:

            created_by_user_id = data.get('created_by_user_id')

            exists_amenity = models.ServiceAmenity.objects.filter(
                service_id=service, amenity_id=amenity
            ).exists()

            if not exists_amenity:
                models.ServiceAmenity.objects.create(
                    service_id=service,
                    amenity_id=amenity,
                    created_by_user_id=created_by_user_id
                )

    def get_or_create_headquarter_service(self, service, headquarter):

        HeadquarterService.objects.get_or_create(
            headquarter_id=headquarter, service_id=service
        )


class ListServices(viewsets.ModelViewSet):
    serializer_class = HeadquarterWithServicesSerializer
    authentication_classes = [TokenAuthentication]
    pagination_class = utils.CustomPagination
    queryset = Headquarter.objects.all()

    def list(self, request: Request, *args, **kwargs):
        # query_page = request.query_params.get('page')
        # latitude = request.query_params.get('latitude')
        # longitude = request.query_params.get('longitude')
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        rating = request.query_params.get('rating')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')

        queryset = self.get_queryset()
        queries = Q()
        additional_filters = {}

        if category:
            queries = queries & Q(
                headquarter_service__service__service_category=category
            )

        if search:
            queries = queries & Q(
                Q(name__icontains=search) |
                Q(headquarter_service__service__name__icontains=search) |
                Q(headquarter_service__service__description__icontains=search)
            )
            additional_filters['name__icontains'] = search
            additional_filters['description__icontains'] = search

        if rating:
            queries = queries & Q(
                headquarter_service__headquarter__rating__gte=rating
            )

        if min_price and max_price:
            additional_filters['price__range'] = (min_price, max_price)

        if queries:
            queryset = queryset.filter(queries).distinct()

        page = self.paginate_queryset(queryset)

        if page is not None:
            # Si hay resultados en la caché, devolverlos
            # cache_key = f'services_list_page_{query_page}'
            # cached_data = cache.get(cache_key)
            # if cached_data is not None:
            #     return self.get_paginated_response(cached_data)

            serializer = self.get_serializer(
                page, many=True, context={
                    'request': request,
                    'additional_filters': additional_filters}
            )
            # Guardar resultados en la caché
            # cache.set(cache_key, serializer.data, timeout=50)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True,
            context={
                'request': request,
                'category': category
            }
        )
        return Response(
            {
                'success': serializer.data
            },
            status=status.HTTP_200_OK
        )


class ListCategoriesServices(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceCategorySerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]

    def list(self, request: Request, *args, **kwargs):
        categories = models.ServiceCategory.objects.all()
        serializer = self.serializer_class(
            categories, many=True, context={'request': request}
        )
        data = serializer.data
        return Response(
            {
                'success': data
            },
            status=status.HTTP_200_OK
        )


class RegisterSimpleAppointment(viewsets.ModelViewSet):
    serializer_class = serializers.SimpleAppointmentSerializer
    authentication_classes = [TokenAuthentication]
    queryset = models.SimpleAppointment.objects.all()

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        data['created_by_user_id'] = request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request: Request, *args, **kwargs):
        user_id = request.user.pk
        date = request.query_params.get('date')

        queryset = self.get_queryset().filter(created_by_user_id=user_id)

        if date:
            queryset = queryset.filter(day_and_time__icontains=date)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': serializer.data}, status=status.HTTP_200_OK)
