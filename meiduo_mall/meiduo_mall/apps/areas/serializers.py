from rest_framework import serializers
from . import models
from users.models import User


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Area
        fields = ("id", "name")


class SubAreaSerializer(serializers.ModelSerializer):
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = models.Area
        fields = ("id", "name", "subs")

class DeliveryAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = '__all__'
