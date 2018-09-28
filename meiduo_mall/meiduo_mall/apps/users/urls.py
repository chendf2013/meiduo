from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [
    url(r'^users/$', views.UserRegister.as_view()),
    url(r'^usernames/(?P<username>.+)/count/$', views.UserNameCheck.as_view()),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCheck.as_view()),
    # 登录获取token 和user
    url(r'^authorizations/$', obtain_jwt_token, name='authorizations'),
    #第一步找回密码 完成图片验证码验证并发起短息验证码发送请求
    url(r'^accounts/(?P<account>\w{5,20})/sms/token/$', views.SMSCodeTokenView.as_view()),
    # 第二步找回密码 发送手机验证码
    url(r'^sms_codes/$', views.SMSCodeByTokenView.as_view()),


]

