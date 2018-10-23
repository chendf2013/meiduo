from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from oauth.utils import OAuthQQ
from users.models import User


class OAuthQQUserSerializer(serializers.Serializer):
    """用户的QQ信息绑定或者直接创建拥有QQ用户信息的用户信息"""
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        """参数校验"""
        # 检验access_token，获取openid
        access_token = attrs['access_token']
        openid = OAuthQQUser.check_save_user_token(access_token)
        if not openid:
            raise serializers.ValidationError('无效的access_token')

        attrs['openid'] = openid
        # 检验短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')
        # 根据手机号进行查询，然后检查密码是否通过
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        """如果没有查询到用户，那就进行创建用户"""
        user = validated_data.get('user')
        if not user:
            # 用户不存在
            user = User.objects.create_user(
                username=validated_data['mobile'],
                password=validated_data['password'],
                mobile=validated_data['mobile'],
            )

        OAuthQQUser.objects.create(
            openid=validated_data['openid'],
            user=user
        )
        return user
