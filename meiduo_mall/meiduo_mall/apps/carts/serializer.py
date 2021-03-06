from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    购物车数据序列化器
    """
    sku_id = serializers.IntegerField(label='sku id ', required=True, min_value=1)
    count = serializers.IntegerField(label='数量', required=True, min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate(self, data):
        try:
            sku = SKU.objects.get(id=data['sku_id'])
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        if data['count'] > sku.stock:
            raise serializers.ValidationError('商品库存不足')

        return data


class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label="数量")
    selected = serializers.BooleanField()
    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count', 'selected')


class CartDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')


        return value




