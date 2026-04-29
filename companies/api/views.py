"""
File for the API views of the companies application
"""
# Third-party Libraries
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response

# Local Modules
from companies import models
from companies.api import serializers
from core import models as core_models
from core import utils as core_utils


class CreateCompany(viewsets.ViewSet):

    serializer_class_company = serializers.CompanySerializer
    serializer_class_company_file = serializers.CompanyFileSerializer
    status_class = status.HTTP_200_OK
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):

        data = request.data.copy()
        created_by_user_id = request.user.pk
        data['created_by_user_id'] = created_by_user_id

        serializer_company = self.get_or_create_company(data)
        data['company_id'] = serializer_company.data['id']
        self.get_or_create_files(data)

        return Response(
            {
                'success': 'Compañia creada exitosamente'
            },
            status=self.status_class
        )

    def get_or_create_company(self, data):

        company_name = data.get('name')
        created_by_user_id = data.get('created_by_user_id')

        company = models.Company.objects.filter(
            name=company_name, created_by_user_id=created_by_user_id
        ).first()

        serializer_company = self.serializer_class_company(instance=company)

        if not company:
            serializer_company = self.serializer_class_company(data=data)
            serializer_company.is_valid(raise_exception=True)
            company = serializer_company.save()
            self.status_class = status.HTTP_201_CREATED

        return serializer_company

    def get_or_create_files(self, data):

        type_file_profile_image = core_models.Type.objects.get_type(
            code='profile_image',
            category_type_code='type_file'
        )

        type_file_cover_image = core_models.Type.objects.get_type(
            code='cover_image',
            category_type_code='type_file'
        )

        data_company_file = []

        company_id = data.get('company_id')
        profile_image = data.get('profile_image')
        cover_image = data.get('cover_image')
        created_by_user_id = data.get('created_by_user_id')

        exists_profile_image = models.CompanyFile.objects.filter(
            company_id=company_id, type_id=type_file_profile_image.id
        ).exists()

        exists_cover_image = models.CompanyFile.objects.filter(
            company_id=company_id, type_id=type_file_cover_image.id
        ).exists()

        if profile_image and not exists_profile_image:
            data_company_file.append(
                {
                    'company_id': company_id,
                    'type_id': type_file_profile_image.id,
                    'file': profile_image,
                    'created_by_user_id': created_by_user_id
                }
            )
        if cover_image and not exists_cover_image:
            data_company_file.append(
                {
                    'company_id': company_id,
                    'type_id': type_file_cover_image.id,
                    'file': cover_image,
                    'created_by_user_id': created_by_user_id
                }
            )

        if data_company_file:
            serializer_company_file = self.serializer_class_company_file(
                data=data_company_file, many=True
            )
            serializer_company_file.is_valid(raise_exception=True)
            serializer_company_file.save()


class CreateHeadquarter(viewsets.ViewSet):

    serializer_class_headquarter = \
        serializers.HeadquarterSerializer
    serializer_class_headquarter_file = \
        serializers.HeadquarterFileSerializer
    status_class = status.HTTP_200_OK
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        created_by_user_id = request.user.pk
        data['created_by_user_id'] = created_by_user_id

        serializer_headquarter = \
            self.get_or_create_headquarter(data=data)
        data['headquarter_id'] = \
            serializer_headquarter.data['id']
        self.get_or_create_files(data=data)
        self.add_headquarter_to_geo_reference(data=data)

        return Response(
            data=serializer_headquarter.data,
            status=self.status_class
        )

    def add_headquarter_to_geo_reference(self, data):

        hq_company = models.Headquarter.objects.get(
            id=data.get('headquarter_id')
        )

        geo_references_city = core_models.GeoReferenceCity.objects.filter(
            city=hq_company.city
        )

        distances = []

        for geo_reference_city in geo_references_city:
            try:
                distance = core_utils.calculate_km_between_two_points(
                    (float(hq_company.latitude),
                     float(hq_company.longitude)),

                    (float(geo_reference_city.latitude),
                     float(geo_reference_city.longitude)))

            except Exception:
                continue

            distances.append((geo_reference_city, distance))

            # Sort positions based on distance
        sorted_positions = sorted(distances, key=lambda x: x[1])

        if len(sorted_positions) > 1:

            hq_company.geo_reference_city = sorted_positions[0][0]
            hq_company.save()

    def get_or_create_headquarter(self, data):
        name_headquarter = data.get('name')
        company_id = data.get('company_id')
        created_by_user_id = data.get('created_by_user_id')

        headquarter = models.Headquarter.objects.filter(
            name=name_headquarter,
            company_id=company_id,
            created_by_user_id=created_by_user_id
        ).first()

        serializer_headquarter = \
            self.serializer_class_headquarter(
                instance=headquarter
            )

        if not headquarter:
            serializer_headquarter = \
                self.serializer_class_headquarter(data=data)
            serializer_headquarter.is_valid(raise_exception=True)
            headquarter = serializer_headquarter.save()
            self.status_class = status.HTTP_201_CREATED

        return serializer_headquarter

    def get_or_create_files(self, data):

        type_file_additional_image = core_models.Type.objects.get_type(
            code='additional_image',
            category_type_code='type_file'
        )

        data_headquarter_file = []

        headquarter_id = data.get('headquarter_id')
        additional_image = self.request.FILES.getlist('additional_image')
        created_by_user_id = data.get('created_by_user_id')

        exists_additional_image = models.HeadquarterFile.objects.filter(
            headquarter_id=headquarter_id,
            type_id=type_file_additional_image.id
        ).exists()

        if additional_image and not exists_additional_image:
            for file in additional_image:
                data_headquarter_file.append(
                    {
                        'headquarter_id': headquarter_id,
                        'type_id': type_file_additional_image.id,
                        'file': file,
                        'created_by_user_id': created_by_user_id
                    }
                )

        if data_headquarter_file:
            serializer_headquarter_file =\
                self.serializer_class_headquarter_file(
                    data=data_headquarter_file, many=True
                )

            serializer_headquarter_file.is_valid(raise_exception=True)
            serializer_headquarter_file.save()


class CreateWeekDayTimeConfigurationCompany(viewsets.ViewSet):
    """
    ViewSet to create a new week day time configuration.
    """
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        usuario = request.user
        headquarter_id = data.pop('headquarter_id')[0]
        week = data.items()

        for day, hours in week:
            if hours:
                self.create_headquartertimeconfiguration(
                    day, hours, headquarter_id, usuario)

        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

    def create_headquartertimeconfiguration(
            self, day, hours, headquarter_id, usuario):

        weekday = day
        times = hours.split(';')

        for time in times:
            start_time, end_time = time.split('-')

            weekday_obj = core_models.WeekDay.objects.filter(
                code=weekday
            ).first()

            time_config, _ = \
                core_models.TimeConfiguration.objects.get_or_create(
                    start_time=start_time,
                    end_time=end_time,
                    defaults={
                        'created_by_user_id': usuario.pk
                    }
                )

            w_d_t_config, _ = \
                core_models.WeekDayTimeConfiguration.objects.get_or_create(
                    week_day=weekday_obj,
                    time_configuration=time_config,
                    defaults={
                        'created_by_user_id': usuario.pk
                    }
                )

            models.HeadquaterWeekDayTimeConfiguration.objects.get_or_create(
                headquarter_id=headquarter_id,
                week_day_time_configuration=w_d_t_config,
                defaults={
                    'created_by_user_id': usuario.pk
                }
            )


class ListCompanies(viewsets.ModelViewSet):

    serializer_class = serializers.CompanySerializer
    authentication_classes = [TokenAuthentication]
    pagination_class = core_utils.CustomPagination
    queryset = models.Company.objects.all()

    def list(self, request: Request, *args, **kwargs):

        query_page = request.query_params.get('page')
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            cache_key = f'companies_list_page_{query_page}'
            cache_data = cache.get(cache_key)

            if cache_data is not None:
                return self.get_paginated_response(cache_data)

            serializer = self.get_serializer(page, many=True)
            cache.set(cache_key, serializer.data, timeout=50)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(
            {
                'success': data
            },
            status=status.HTTP_200_OK
        )


class HeadquarterLike(viewsets.ViewSet):
    """
    ViewSet to create a new week day time configuration.
    """
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        headquarter_id = request.data.get('headquarter_id')
        headquarter = models.Headquarter.objects.filter(
            id=headquarter_id
        ).first()

        if not headquarter:
            return Response(
                {'error': 'Headquarter  not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        models.HeadquarterLike.objects.get_or_create(
            headquarter=headquarter,
            user=request.user,
            created_by_user_id=request.user.pk
        )

        return Response({'success': '¡Liked!'}, status=status.HTTP_201_CREATED)


class HeadquarterDislike(viewsets.ViewSet):
    """
    ViewSet to create a new week day time configuration.
    """
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        headquarter_id = request.data.get('headquarter_id')
        headquarter = models.Headquarter.objects.filter(
            id=headquarter_id
        ).first()

        if not headquarter:
            return Response(
                {'error': 'Headquarter  not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        models.HeadquarterLike.objects.filter(
            headquarter=headquarter,
            user=request.user
        ).delete()

        return Response({'success': 'Dislike'},
                        status=status.HTTP_202_ACCEPTED
                        )
