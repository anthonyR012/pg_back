# Python Standard Library
import os
import requests
import time
from datetime import datetime

# Third-party Libraries
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.utils import timezone
from fcm_django.models import FCMDevice
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

# Local Modules
from users import models
from users import tasks
from users.api import serializers


# Create your views here.
class CustomAuthToken(ObtainAuthToken):
    serializer_class = serializers.BaseUserSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request: Request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        user = authenticate(
            request=request, username=username, password=password)
        if not user:
            return Response(
                {
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.serializer_class(
            user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        token, created = Token.objects.get_or_create(user=user)

        serialized_data = serializer.data
        serialized_data['token'] = token.key

        return Response(
            {
                'success': 'Login exitoso',
                'user': serialized_data,
            },
            status=status.HTTP_200_OK
        )


class RegistrationOauthAPI(viewsets.ViewSet):
    serializer_class = serializers.RegisterUserSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        access_token_google = data.get('access_google_token')
        email = data.get('email')
        url_picture = data.get('picture')

        google_token_valid = self.validate_google_token(
            access_token_google, email
        )
        if not google_token_valid:
            return Response(
                {
                    'error': 'Invalid Google Token'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = models.User.objects.filter(email=email).first()
        if user:
            return self.handle_existing_user(user)

        data['picture'] = self.get_google_picture(url_picture)

        return self.handle_new_user(data)

    def validate_google_token(self, access_token, email):
        token_validation = requests.get(
            f'https://oauth2.googleapis.com/'
            f'tokeninfo?access_token={access_token}'
        )

        if token_validation.status_code == status.HTTP_200_OK:
            user_info = token_validation.json()
            if user_info.get('email') == email:
                return True

        return False

    def get_google_picture(self, url_picture):
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                response = requests.get(url_picture, stream=True)
                response.raise_for_status()

                filename = os.path.basename(url_picture)
                picture = ContentFile(response.content, name=filename)
                return picture

            except requests.exceptions.RequestException:
                if attempt == max_attempts - 1:
                    # Could not download picture
                    return None

                # Could not download picture. Retrying...
                time.sleep(1)

    def handle_existing_user(self, user: models.User):
        token, created = Token.objects.get_or_create(user=user)

        serializer_data = self.serializer_class(
            user, context={'request': self.request}
        ).data
        serializer_data['token'] = token.key

        return Response(
            {
                'success': 'Usuario registrado exitosamente',
                'user': serializer_data
            },
            status=status.HTTP_200_OK
        )

    def handle_new_user(self, data):
        serializer = self.serializer_class(
            data=data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)

        user: models.User = serializer.save()
        user.email_verified = True
        user.save()

        token, created = Token.objects.get_or_create(user=user)

        # TODO: Add FCM registration
        try:
            # https://fcm-django.readthedocs.io/en/latest/
            registration_id = data.get('registration_id')
            device_id = data.get('device_id')
            type_device = data.get('type_device')  # 'android', 'web' or 'ios'

            FCMDevice.objects.create(
                registration_id=registration_id,
                device_id=device_id,
                type=type_device,
                user=user
            )

        except Exception as e:
            print(e)

        serializer_data = serializer.data
        serializer_data['token'] = token.key

        return Response(
            {
                'success': 'Usuario registrado exitosamente',
                'user': serializer_data
            },
            status=status.HTTP_201_CREATED
        )


class RegistrationAlternateAPI(viewsets.ViewSet):
    serializer_class = serializers.RegisterUserSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        email = data.get('email')
        picture = data.get('picture')

        if not picture or picture == '':
            data['picture'] = None

        user = models.User.objects.filter(email=email).first()
        if user:
            return Response(
                {
                    'error': 'Ya existe un usuario con el correo ingresado'
                },
                status=status.HTTP_409_CONFLICT
            )

        serializer = self.serializer_class(
            data=data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)

        # TODO: Add FCM registration
        try:
            # https://fcm-django.readthedocs.io/en/latest/
            registration_id = data.get('registration_id')
            device_id = data.get('device_id')
            type_device = data.get('type_device')  # 'android', 'web' or 'ios'

            FCMDevice.objects.create(
                registration_id=registration_id,
                device_id=device_id,
                type=type_device,
                user=user
            )

        except Exception as e:
            print(e)

        serializer_data = serializer.data
        serializer_data['token'] = token.key

        tasks.verification_email_user.delay(user.pk)

        return Response(
            {
                'success': 'Usuario registrado exitosamente, '
                           'se ha enviado un correo de verificación',
                'user': serializer_data,
            },
            status=status.HTTP_201_CREATED
        )


class BaseVerifyEmail(viewsets.ViewSet):

    def handle_verification_code(self, user, code):
        if not user:
            return Response(
                {
                    'error': 'No existe un usuario con el correo ingresado'
                },
                status=status.HTTP_409_CONFLICT
            )

        verification_code = models.UserVerificationCode.objects.filter(
            user=user, code=code
        ).first()

        if not verification_code:
            return Response(
                {
                    'error': 'Código inválido'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if verification_code.valid_until < timezone.now():
            return Response(
                {
                    'error': 'Código expirado'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.email_verified = True
        user.save()

        return user


class VerifyEmail(BaseVerifyEmail):
    serializer_class = serializers.BaseUserSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        code = data.get('code')
        user = request.user

        result = self.handle_verification_code(user, code)
        if isinstance(result, Response):
            return result

        token, created = Token.objects.get_or_create(user=user)

        serializer = self.serializer_class(user, context={'request': request})
        serialized_data = serializer.data
        serialized_data['token'] = token.key

        return Response(
            {
                'success':  'Correo verificado exitosamente',
                'user': serialized_data
            },
            status=status.HTTP_200_OK
        )


class ForwardVerificationEmail(viewsets.ViewSet):
    serializer_class = serializers.BaseUserSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        user = request.user

        token, created = Token.objects.get_or_create(user=user)

        serializer = self.serializer_class(user, context={'request': request})
        serializer_data = serializer.data
        serializer_data['token'] = token.key

        tasks.verification_email_user.delay(user.pk)

        return Response(
            {
                'success': 'Se ha enviado un correo de verificación.',
                'user': serializer_data,
            },
            status=status.HTTP_201_CREATED
        )


class RequestRecoverUser(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        email = data.get('email')

        user = models.User.objects.filter(email=email).first()
        if not user:
            return Response(
                {
                    'error': 'No existe un usuario con el correo ingresado'
                },
                status=status.HTTP_409_CONFLICT
            )

        tasks.verification_email_recover_user.delay(user.pk)

        return Response(
            {
                'success': 'Se ha enviado un codigo de recuperación al '
                           'correo ingresado'
            },
            status=status.HTTP_200_OK
        )


class VerifyEmailRecoverUser(BaseVerifyEmail):
    serializer_class = serializers.BaseUserSerializer
    permission_classes = [AllowAny]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        code = data.get('code')
        email = data.get('email')

        user = models.User.objects.filter(email=email).first()

        result = self.handle_verification_code(user, code)
        if isinstance(result, Response):
            return result

        token, created = Token.objects.get_or_create(user=user)

        serializer = self.serializer_class(user, context={'request': request})
        serialized_data = serializer.data
        serialized_data['token'] = token.key

        return Response(
            {
                'success':  'Correo verificado exitosamente',
                'user': serialized_data
            },
            status=status.HTTP_200_OK
        )


class UpdatePassword(viewsets.ViewSet):
    serializer_class = serializers.UpdatePasswordSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        user = request.user

        serializer = self.serializer_class(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': 'Contraseña actualizada exitosamente'
            },
            status=status.HTTP_200_OK
        )


class UpdateUserInfo(viewsets.ViewSet):
    serializer_class = serializers.UpdateUserInfoSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        date_of_birth = data.get('date_of_birth')

        try:
            date_of_birth = datetime.strptime(date_of_birth, '%d/%m/%Y').date()
        except ValueError:
            date_of_birth = None

        data['date_of_birth'] = date_of_birth

        serializer = self.serializer_class(user, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': 'Información actualizada exitosamente',
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )


class CreateUserAddress(viewsets.ViewSet):
    serializer_class = serializers.CreateUserAddressSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        user = request.user
        data['user'] = user.pk
        data['created_by_user_id'] = user.pk

        user_address = models.UserAddress.objects.filter(
            user=user,
            address=data['address']
        ).first()

        serializer = self.serializer_class(instance=user_address, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': 'Dirección registrada exitosamente',
                'address': serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class UpdateUserAddress(viewsets.ViewSet):
    serializer_class = serializers.UpdateUserAddressSerializer
    authentication_classes = [TokenAuthentication]

    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        user_address = data.get('user_address_id')

        if not user_address:
            return Response(
                {
                    'error': 'user_address_id es requerido'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user_address = models.UserAddress.objects.filter(
            id=user_address).first()

        serializer = self.serializer_class(instance=user_address, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': 'Dirección actualizada exitosamente',
                'address': serializer.data
            },
            status=status.HTTP_200_OK
        )


class ListUserAddresses(viewsets.ViewSet):
    serializer_class = serializers.ListUserAddressSerializer
    authentication_classes = [TokenAuthentication]

    def list(self, request: Request, *args, **kwargs):
        user = request.user
        addresses = models.UserAddress.objects.filter(user=user)

        serializer = self.serializer_class(addresses, many=True)

        return Response(
            {
                'success': serializer.data
            },
            status=status.HTTP_200_OK
        )
