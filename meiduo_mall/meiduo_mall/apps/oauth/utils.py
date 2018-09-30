import logging
from urllib.parse import urlencode

from django.conf import settings

logger = logging.getLogger("django")



class OAuthQQ(object):
    """用于在Python代码中实现发送请求"""
    def __init__(self,app_id=None,app_key=None,redirect_uri=None,state=None):
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
