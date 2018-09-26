import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """
    定义用户的序列化器
    # 添加额外字段
    # 将原有继承字段进行约束限制
    # 重写校验方法
    # 重写保存方法
    """
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label="短信验证码",required=True,allow_null=False,allow_blank=False,write_only=True)
    allow = serializers.CharField(label="同意协议",required=True,allow_null=False,allow_blank=False,write_only=True)


    # id  read_only
    # username 长短限制（5-20）,不能为空，不能是空字符串
    # password 长短限制（8-20)，不能为空，不能是空字符串，write_only
    # mobile 是否是11为手机号码
    # 忘记了重写类和 模型 字段范围
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow')
        kwargs_extra={
        "id":{
            "read_only":True
        },
        "username":{
             "max_length":20,
            "min_length":5,
            "required":True,
            "allow_null":False,
            "allow_blank":False,
            "error-messages":{
                # 用户名长度不符合要求
                'min_length': '仅允许5-20个字符的用户名',
                'max_length': '仅允许5-20个字符的用户名',
            }
        },
        "password":{
            "max_length": 20,
            "min_length": 8,
            "required": True,
            "allow_null": False,
            "allow_blank": False,
            "write_only":True,
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
        if not re.match(r"^1[345789]\d{9}$",value):
        # 手机号码不正确
            raise serializers.ValidationError('手机号码格式不正确')
        return value
    def validate_allow(self,value):
        if value != "true":
            # 同意不正确
            raise serializers.ValidationError('请同意协议内容')
        return value



    def validate(self,data):
        print("其他数据验证")
        # password2 是否等于passwod
        password=data["password"]
        password2=data["password2"]
        if password2 != password:
        # 密码不正确报错
            raise serializers.ValidationError('两次密码不一致')
        # sms_code 是否等于在redis中保存的值(忘记了没有获取到验证码的情况)
        mobile= data["mobile"]
        sms_code = data["sms_code"]
        redis_cnn = get_redis_connection('verify_codes')
        # real_sms_code = redis_cnn.get("sms_%s" % mobile)
        real_sms_code = redis_cnn.get("sms_%s" % mobile).decode()
        if not real_sms_code:
            raise serializers.ValidationError('没有获取到验证码')
        if real_sms_code!=sms_code:
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
    # def create(self, validated_data):
    #     print("保存数据")
    #     # 去掉不用保存的字段（password2,sms_code,allow）
    #     del validated_data["password2"]
    #     del validated_data["sms_code"]
    #     del validated_data["allow"]
    #     # user = super().create(validated_data)
    #     user = super().create(validated_data)
    #     # 密码加密
    #     user.set_password(validated_data['password'])
    #     # 保存
    #     user.save()
    #     return user

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()

        return user