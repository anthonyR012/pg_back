# Python Standard Library

# Third-party Libraries
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Local Modules
from users import models


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = '__all__'
        read_only_fields = [
            'pk', 'first_name', 'last_name', 'email', 'is_superuser',
            'is_active', 'is_staff', 'date_joined'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'picture': {'required': False},
            'password': {'write_only': True},
        }


class RegisterUserSerializer(BaseUserSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=models.User.objects.all()
            )
        ]
    )

    password = serializers.CharField(write_only=True, required=True)

    def create(self, validated_data):
        user = models.User.objects.create(
            username=validated_data.get('email'),
            email=validated_data.get('email'),
            full_name=validated_data.get('full_name'),
            phone=validated_data.get('phone'),
            picture=validated_data.get('picture'),
            uuid_google=validated_data.get('uuid_google')
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UpdateUserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'pk', 'email', 'full_name', 'phone', 'address', 'gender',
            'city', 'date_of_birth'
        )

        read_only_fields = ['pk']
        extra_kwargs = {
            'full_name': {'required': False},
            'phone': {'required': False},
            'address': {'required': False},
            'gender': {'required': False},
            'city': {'required': False},
        }


class UpdatePasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            'pk', 'password'
        )

        read_only_fields = ['pk']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class CreateUserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserAddress
        fields = (
            'pk', 'user', 'address', 'type', 'latitude', 'longitude',
            'created_by_user_id',
        )

        read_only_fields = ['pk']


class UpdateUserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserAddress
        fields = (
            'pk', 'address', 'type', 'latitude', 'longitude'
        )

        read_only_fields = ['pk']


class ListUserAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserAddress
        fields = (
            'pk', 'address', 'type', 'latitude', 'longitude'
        )

        read_only_fields = ['pk']
