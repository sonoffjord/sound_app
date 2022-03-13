from dataclasses import fields
from rest_framework import serializers

from . import models


class UserSerializer(serializers.Serializer):
    class Meta:
        model = models.AuthUser
        fields = ('avatar', 'country', 'city', 'bio', 'display_name')


class SocialLinkSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.SocialLink
        fields = ('id', 'link')


class AuthorSerializer(serializers.Serializer):
    social_links = SocialLinkSerializer(many=True)

    class Meta:
        model = models.AuthUser
        fields = ('id', 'avatar', 'country', 'city', 'bio', 'display_name', 'social_links')


class GoogleAuth(serializers.Serializer):
    """ Сериализация данных от Google """

    email = serializers.EmailField()
    token = serializers.CharField()
