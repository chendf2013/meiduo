from django.db.migrations import serializer
from django_redis import get_redis_connection
from redis import RedisError
from requests import Response
from rest_framework import serializers
import logging
# import RedisError

logger = logging.getLogger("django")


class SmsCodeSerializer(serializers.Serializer):
    """定义序列化器"""

    # 手机号在路径的正则表达式校验过
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        """进行验证码校验"""
        # 获取参数
        image_code_id = attrs["image_code_id"]
        text = attrs["text"]
        # 根据随机编码获取验证码
        rediscn= get_redis_connection("verify_codes")
        # try:
        real_text = rediscn.get("img_%s" % image_code_id)
        # except Exception as ret:
        #     raise serializers.ValidationError("数据库获取图片验证码错误")

        if not real_text:
            # 过期或者不存在
            raise serializers.ValidationError("无效的图片验证码")


        # 对比
        #　redis 储存的是二进制字节码，需要进行解码
        real_text = real_text.decode()
        if real_text.lower()!=text.lower():
            raise serializers.ValidationError("图片验证码错误")
        try:
            # 删除redis中的图片验证码，防止多次请求验证
            rediscn.delete("img_%s"% image_code_id)
        except RedisError as ret:
            logger.error(ret)


        # 是否发送过短信标志
        mobile = self.context["view"].kwargs["mobile"]
        sms_flag = rediscn.get("send_flag_%s"%mobile)


        if sms_flag:
            raise serializers.ValidationError("请求手机验证码过于频繁")
        return attrs