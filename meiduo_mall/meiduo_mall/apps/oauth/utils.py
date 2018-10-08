import json
import logging
import re
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from django.conf import settings

from oauth import constants
from oauth.exceptions import QQAPIException
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData, Serializer

logger = logging.getLogger("django")


class OAuthQQ(object):
    """用于在Python代码中实现发送请求"""

    def __init__(self, app_id=None, app_key=None, redirect_uri=None, state=None):
        self.app_id = app_id or settings.QQ_APP_ID
        self.app_key = app_key or settings.QQ_APP_KEY
        self.redirect_url = redirect_uri or settings.QQ_REDIRECT_URL
        self.state = state or '/'  # 用于保存登录成功后的跳转页面路径

    def get_auth_url(self):
        """
        获取qq登录的网址
        :return: url
        """
        params = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.redirect_url,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_auth_accsess(self, code):
        """
        获取用户的access_token
        :param code: qq返回的code
        :return: access_token
        """
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_url
        }
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        response = urlopen(url)
        # 先读取再解码
        response_data = response.read().decode()
        # 将之转换为字典形式
        data = parse_qs(response_data)
        access_token = data.get("access_token", None)
        if not access_token:
            logger.error("code=%s,msg=%s" % (data.get("code"), data.get("msg")))
            # 定义一个错误信息
            raise QQAPIException
        # 返回的是个列表信息，我们只需要第一个参数
        return access_token[0]

    def get_auth_openid(self, access_token):
        """
              获取用户的openid
              :param access_token: qq返回的access_token
              :return: 获取用户的openid
              """

        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        # 先读取再解码
        response_data = response.read().decode()
        # 返回的是json格式字符串
        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = re.match(r"^callback\( (.*) \);$", response_data).group(1)
            data = json.loads(data)
        except Exception as ret:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException
        openid = data.get("openid")
        return openid


