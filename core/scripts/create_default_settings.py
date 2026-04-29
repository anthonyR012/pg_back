"""
python manage.py shell < core/scripts/create_default_settings.py
"""

# Python Standard Library
import json

# Third-party Libraries
from cities_light.models import City
from django.core.exceptions import MultipleObjectsReturned
from django.core.management import call_command
from django.db import transaction

# Local Modules
from companies.scripts import create_default_settings as cds_companies
from core import models
from services.scripts import create_default_settings as cds_services
from users import models as user_models
from users.scripts import create_default_settings as cds_users

f = open('core/scripts/default_settings.json')
default_settings = json.load(f)

CATEGORIES_TYPES = default_settings.get('categories_types', None)
WEEK_DAYS = default_settings.get('week_days', None)
AMENITIES = default_settings.get('amenities', None)


def create_categories_types():

    print('################# CREATING TYPES ################')
    with transaction.atomic():

        try:

            created_by_user = user_models.User.objects.filter(
                username='admin'
            ).last()

            if not created_by_user:
                raise ValueError(
                    'Field "created_by_user" in categorys is mandatory'
                )

            for category_types in CATEGORIES_TYPES:

                code = category_types.get('code', None)
                description = category_types.get('description', None)

                types = category_types.get('types', None)

                category, created = models.Category.objects.update_or_create(
                    defaults={
                        'code': code,
                        'description': description,
                        'created_by_user_id': created_by_user.pk
                    },
                    **{
                        'code': code
                    }
                )

                if created:
                    print(f'Category {category} created.')
                else:
                    print(f'Category {category} updated.')

                for type in types:
                    code = type.get('code', None)
                    description = type.get('description', None)

                    type, created = models.Type.objects.update_or_create(
                        defaults={
                            'description': description,
                            'created_by_user_id': created_by_user.pk
                        },
                        **{'category_type': category, 'code': code}
                    )

                    if created:
                        print(f'Type {type} created.')
                    else:
                        print(f'Type {type} updated.')

        except ValueError as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except MultipleObjectsReturned as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except Exception as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)


def create_week_days():

    print('################# CREATING WEEK DAYS ################')
    with transaction.atomic():

        try:

            created_by_user = user_models.User.objects.filter(
                username='admin'
            ).last()

            if not created_by_user:
                raise ValueError(
                    'Field "created_by_user" in categorys is mandatory'
                )

            for week_day_data in WEEK_DAYS:

                code = week_day_data.get('code', None)
                description = week_day_data.get('description', None)

                week_day, created = models.WeekDay.objects.update_or_create(
                    defaults={
                        'code': code,
                        'description': description,
                        'created_by_user_id': created_by_user.pk
                    },
                    **{
                        'code': code
                    }
                )

                if created:
                    print(f'Week day {week_day} created.')
                else:
                    print(f'Week day {week_day} updated.')

        except ValueError as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except MultipleObjectsReturned as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except Exception as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)


def create_geo_references_cities():

    print('################# CREATING GEO REFERENCES CITIES ################')
    with transaction.atomic():

        try:
            created_by_user = user_models.User.objects.filter(
                username='admin'
            ).last()

            if not created_by_user:
                raise ValueError(
                    'Field "created_by_user" in categorys is mandatory'
                )

            cities = City.objects.all()
            if not cities:
                print('############### CREATING CITIES LIGHT ###############')
                call_command('cities_light')
                print('################ CITIES LIGHT CREATED ################')
                cities = City.objects.all()

            for city in cities:

                geo_reference_city, created = \
                    models.GeoReferenceCity.objects.get_or_create(
                        name=f'{city.name}',
                        city=city,
                        created_by_user_id=created_by_user.pk,
                        defaults={
                            'latitude': city.latitude,
                            'longitude': city.longitude
                        }
                    )

                if created:
                    print(f'Geo reference city {city.name} created')
                else:
                    print(f'Geo reference city {city.name} updated')

        except ValueError as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except MultipleObjectsReturned as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except Exception as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)


def create_amenities():

    print('################# CREATING AMENITIES ################')
    with transaction.atomic():

        try:

            created_by_user = user_models.User.objects.filter(
                username='admin'
            ).last()

            if not created_by_user:
                raise ValueError(
                    'Field "created_by_user" in categorys is mandatory'
                )

            for amenity_data in AMENITIES:

                code = amenity_data.get('code', None)
                description = amenity_data.get('description', None)
                color = amenity_data.get('color', None)
                icon_name = amenity_data.get('icon_name', None)

                amenity, created = models.Amenity.objects.update_or_create(
                    defaults={
                        'code': code,
                        'description': description,
                        'color': color,
                        'icon_name': icon_name,
                        'created_by_user_id': created_by_user.pk
                    },
                    **{
                        'code': code
                    }
                )

                if created:
                    print(f'Amenity {amenity} created.')
                else:
                    print(f'Amenity {amenity} updated.')

        except ValueError as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except MultipleObjectsReturned as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except Exception as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)


cds_users.create_user_admin()
create_categories_types()
create_week_days()
create_geo_references_cities()
create_amenities()
cds_users.run()
cds_companies.run()
cds_services.run()
