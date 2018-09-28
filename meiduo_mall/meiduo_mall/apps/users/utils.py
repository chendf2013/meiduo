import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }



def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    try:
        user = User.objects.get(mobile=account)
        return user
    except:
        try:
            user = User.objects.get(username=account)
            return user
        except User.DoesNotExist:
            return None


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 当前的username 并不一定是username 有可能还是电话号码
        # 获取当前用户
        user = get_user_by_account(username)
        # 自动实现密码校验
        if user is not None and user.check_password(password):
            # 将当前用户返回
            return user