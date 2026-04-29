# Python Standard Library
import json
import os

# Third-party Libraries
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from cities_light.models import Country

# Local Modules
from companies import models
from users import models as user_models
from core import models as core_models
from ponteglam.settings import BASE_DIR

f = open('companies/scripts/default_settings.json')
default_settings = json.load(f)

COMPANIES = default_settings.get('companies', None)
COMPANIES_IMAGES = os.path.join(
    BASE_DIR, 'static/default_settings/companies_images/'
)


def create_companies():

    print('################# CREATING COMPANIES ################')
    with transaction.atomic():

        try:

            for company_data in COMPANIES:

                name = company_data.get('name', None)
                description = company_data.get('description', None)
                created_by_user = company_data.get(
                    'created_by_user', None
                )
                type = company_data.get('type', None)
                state = company_data.get('state', None)
                picture_filename = company_data.get('picture', None)

                created_by_username = created_by_user
                user = user_models.User.objects.filter(
                    username=created_by_username
                ).last()

                if not user:
                    print(f'Error: User "{created_by_username}" not found. Skipping company "{name}".')
                    continue

                try:
                    type_obj = core_models.Type.objects.get(
                        code=type, category_type__code='type_company'
                    )
                    state_obj = core_models.Type.objects.get(
                        code=state, category_type__code='status_company'
                    )
                except core_models.Type.DoesNotExist as e:
                    print(f'Error: Type/State not found for company "{name}": {e}. Skipping.')
                    continue

                company, created = models.Company.objects.update_or_create(
                    defaults={
                        'name': name,
                        'description': description,
                        'type': type_obj,
                        'state': state_obj,
                        'created_by_user_id': user.pk
                    },
                    **{
                        'name': name
                    }
                )

                picture_path = os.path.join(
                    COMPANIES_IMAGES, picture_filename
                )

                type_file = core_models.Type.objects.get(
                    code='profile_image',
                    category_type__code='type_file'
                )

                with open(picture_path, 'rb') as picture_data:
                    company_file = models.CompanyFile.objects.filter(
                        company=company,
                        type=type_file
                    )

                    for obj in company_file:
                        obj.delete()

                    company_file = models.CompanyFile.objects.create(
                        company=company,
                        type=type_file,
                        created_by_user_id=user.pk
                    )

                    company_file.file.save(picture_filename, picture_data)
                    company_file.save()

                if created:
                    print(f'Company {company} created.')
                else:
                    print(f'Company {company} updated.')

                headquarters = company_data.get('headquarters', None)
                for headquarter_data in headquarters:

                    name = headquarter_data.get('name', None)
                    phone_number = headquarter_data.get('phone_number', None)
                    address = headquarter_data.get('address', None)
                    latitude = headquarter_data.get('latitude', None)
                    longitude = headquarter_data.get('longitude', None)
                    rating_count = headquarter_data.get('rating_count', None)
                    rating = headquarter_data.get('rating', None)
                    geo_reference_city = headquarter_data.get(
                        'geo_reference_city', None
                    )
                    type = headquarter_data.get('type', None)
                    state = headquarter_data.get('state', None)
                    country = headquarter_data.get('country', None)
                    picture_filenames = headquarter_data.get(
                        'pictures', None
                    )

                    geo_reference_city_name = geo_reference_city
                    geo_reference_city_obj = \
                        core_models.GeoReferenceCity.objects.filter(
                            name=geo_reference_city_name
                        ).first()
                    
                    if not geo_reference_city_obj:
                        print(f'Error: Geo Reference City "{geo_reference_city_name}" not found. Skipping headquarter "{name}".')
                        continue

                    try:
                        type_obj = core_models.Type.objects.get(
                            code=type, category_type__code='type_headquarter'
                        )
                        state_obj = core_models.Type.objects.get(
                            code=state, category_type__code='status_headquarter'
                        )
                        country_obj = Country.objects.get(
                            name=country
                        )
                    except (core_models.Type.DoesNotExist, Country.DoesNotExist) as e:
                        print(f'Error: Type/Country not found for headquarter "{name}": {e}. Skipping.')
                        continue

                    headquarter, created = \
                        models.Headquarter.objects.update_or_create(
                            defaults={
                                'company': company,
                                'created_by_user_id': user.pk,
                                'name': name,
                                'phone_number': phone_number,
                                'address': address,
                                'latitude': latitude,
                                'longitude': longitude,
                                'rating_count': rating_count,
                                'rating': rating,
                                'geo_reference_city': geo_reference_city_obj,
                                'type': type_obj,
                                'state': state_obj,
                                'country': country_obj
                            },
                            **{
                                'company': company,
                                'name': name
                            }
                        )

                    contador = 1
                    for picture_filename in picture_filenames:

                        if contador == 1:
                            type_file = core_models.Type.objects.get(
                                code='profile_image',
                                category_type__code='type_file'
                            )
                        else:
                            type_file = core_models.Type.objects.get(
                                code='additional_image',
                                category_type__code='type_file'
                            )

                        picture_path = os.path.join(
                            COMPANIES_IMAGES, picture_filename
                        )

                        with open(picture_path, 'rb') as picture_data:
                            headquarter_file = \
                                models.HeadquarterFile.objects.filter(
                                    headquarter=headquarter,
                                    type=type_file
                                )

                            for obj in headquarter_file:
                                obj.delete()

                            headquarter_file = \
                                models.HeadquarterFile.objects.create(
                                    headquarter=headquarter,
                                    type=type_file,
                                    created_by_user_id=user.pk
                                )

                            headquarter_file.file.save(
                                picture_filename, picture_data
                            )
                            headquarter_file.save()

                            contador += 1

                    if created:
                        print(f'Headquarter {headquarter} created.')
                    else:
                        print(f'Headquarter {headquarter} updated.')

        except ValueError as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except MultipleObjectsReturned as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)

        except Exception as e:
            print(f'Error: {e}')
            transaction.set_rollback(True)


def run():
    create_companies()
