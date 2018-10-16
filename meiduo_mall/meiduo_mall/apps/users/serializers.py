import re

from celery_tasks.email.tasks import send_verify_email
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.settings import api_settings

from goods.models import SKU
from users import constants
from users.models import User, Address
from users.utils import get_user_by_account


class UserSerializer(ModelSerializer):
    """
    定义用户的序列化器
    # 添加额外字段
    # 将原有继承字段进行约束限制
    # 重写校验方法
    # 重写保存方法
    """
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label="短信验证码", required=True, allow_null=False, allow_blank=False, write_only=True)
    allow = serializers.CharField(label="同意协议", required=True, allow_null=False, allow_blank=False, write_only=True)
    # 定义token字段
    token = serializers.CharField(label="token值", read_only=True)

    class Meta:
        model = User
        # 添加token字段
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')

        kwargs_extra = {
            "id": {
                "read_only": True
            },
            "username": {
                "max_length": 20,
                "min_length": 5,
                "required": True,
                "allow_null": False,
                "allow_blank": False,
                "error-messages": {
                    # 用户名长度不符合要求
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            "password": {
                "max_length": 20,
                "min_length": 8,
                "required": True,
                "allow_null": False,
                "allow_blank": False,
                "write_only": True,
                "erro-message": {
                    # 密码长度不符合要求
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            },
            # "mobile":{
            #     "max_length": 11,
            #     "min_length": 11,
            #     "required": True,
            #     "allow_null": False,
            #     "allow_blank": False,
            # }
        }

    def validate_mobile(self, value):
        if not re.match(r"^1[345789]\d{9}$", value):
            # 手机号码不正确
            raise serializers.ValidationError('手机号码格式不正确')
        return value

    def validate_allow(self, value):
        if value != "true":
            # 同意不正确
            raise serializers.ValidationError('请同意协议内容')
        return value

    def validate(self, data):
        # password2 是否等于passwod
        password = data["password"]
        password2 = data["password2"]
        if password2 != password:
            # 密码不正确报错
            raise serializers.ValidationError('两次密码不一致')
        # sms_code 是否等于在redis中保存的值(忘记了没有获取到验证码的情况)
        mobile = data["mobile"]
        sms_code = data["sms_code"]
        redis_cnn = get_redis_connection('verify_codes')
        # real_sms_code = redis_cnn.get("sms_%s" % mobile)
        real_sms_code = redis_cnn.get("sms_%s" % mobile)
        if not real_sms_code:
            raise serializers.ValidationError('没有获取到验证码')
        if real_sms_code.decode() != sms_code:
            # 短信验证码不正确报错
            raise serializers.ValidationError('短信验证码错误')
        return data

        # mobile 是否是11为手机号码
        # mobile = str(mobile)
        # if not re.match(r"1[345789]\d{9}",mobile):
        # # 手机号码不正确
        #     raise serializers.ValidationError('手机号码格式不正确')

        # allow 是否是false和ture中的一个
        # allow = data["allow"].decode()
        # if allow!="ture":
        #     # 同意不正确
        #     raise serializers.ValidationError('请同意协议内容')

    # def save(self,data):
    def create(self, validated_data):
        # 去掉不用保存的字段（password2,sms_code,allow）
        del validated_data["password2"]
        del validated_data["sms_code"]
        del validated_data["allow"]
        # user = super().create(validated_data)
        user = super().create(validated_data)
        # 密码加密
        user.set_password(validated_data['password'])
        # 保存，会将user添加到当前的序列化器中去
        user.save()

        # 生成token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 将用户的信息添加载荷中去，生成payload信息
        payload = jwt_payload_handler(user)
        # 将对应的载荷生成token
        token = jwt_encode_handler(payload)
        # 将token保存到user对象中，可以才返回给前端
        user.token = token

        return user

    # id  read_only
    # username 长短限制（5-20）,不能为空，不能是空字符串
    # password 长短限制（8-20)，不能为空，不能是空字符串，write_only
    # mobile 是否是11为手机号码
    # 忘记了重写类和 模型 字段范围



class CheckSMSCodeSerializer(serializers.Serializer):
    """
    检查sms code
    """
    sms_code = serializers.CharField(min_length=6, max_length=6)

    # 额外验证短信验证码
    def validate_sms_code(self, value):
        # 获取user
        # 先拿到类视图的实例化对象
        # 然后再使用参数获取用户
        account = self.context['view'].kwargs.get('account')
        user = get_user_by_account(account)
        if user is None:
            raise serializers.ValidationError('用户不存在')
        # 给当前的实例化对象添加user对象,保存user的信息
        self.user = user
        # 根据用户获取短信验证码
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % user.mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if value != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')
        # 验证成功后返回
        return value


class ResetPasswordSerializer(serializers.ModelSerializer):
    """
    重置密码序列化器
    """
    password2 = serializers.CharField(label='确认密码', write_only=True)
    access_token = serializers.CharField(label='操作token', write_only=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'password2', 'access_token')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        """
        校验数据
        """
        # 判断两次密码
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断access token
        allow = User.check_set_password_token(attrs['access_token'], self.context['view'].kwargs['pk'])
        if not allow:
            raise serializers.ValidationError('无效的access token')

        return attrs

    def update(self, instance, validated_data):
        """
        更新密码
        """
        # 调用django 用户模型类的设置密码方法
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'email']
        extra_kwargs = {
            'email': {
                "required": True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()

        # 生成激活链接
        verify_url = instance.generate_email_verify_url()

        # 发送验证邮件
        send_verify_email.delay(instance.email, verify_url)
        return instance



class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validated_data):
        """
        保存
        """
        # Address模型类中有user属性，将user对象添加到模型类的创建参数中
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)


class AddUserBrowsingHistorySerializer(serializers.Serializer):
    """
    添加用户浏览历史序列化器
    """
    sku_id = serializers.IntegerField(label="商品SKU编号", min_value=1, required=True)

    def validate_sku_id(self, value):
        """
        检验sku_id是否存在
        """
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('该商品不存在')
        return value

    def create(self, validated_data):
        """
        保存
        """
        user_id = self.context['request'].user.id
        sku_id = validated_data['sku_id']
        redis_conn = get_redis_connection("history")
        # 移除已经存在的本商品浏览记录
        redis_conn.lrem("history_%s" % user_id, 0, sku_id)
        # 添加新的浏览记录
        redis_conn.lpush("history_%s" % user_id, sku_id)
        # 只保存最多5条记录
        redis_conn.ltrim("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT-1)

        return validated_data