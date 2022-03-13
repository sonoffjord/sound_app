from dataclasses import fields
from rest_framework import serializers

from . import models


class UserSerializer(serializers.Serializer):
    class Meta:
        model = models.AuthUser
        fields = ('avatar', 'country', 'city', 'bio', 'display_name')

class GoogleAuth(serializers.Serializer):
    """ Сериализация данных от Google """

    email = serializers.EmailField()
    token = serializers.CharField()
