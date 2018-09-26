from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^users/$', views.UserRegister.as_view()),
    url(r'^usernames/(?P<username>.+)/count/$', views.UserNameCheck.as_view()),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCheck.as_view()),
# /mobiles/17699243758/count/

    # http://127.0.0.1:8000/users/(注册)
    # this.host + this.username + '/count/'(重名)
    # this.host+'/mobiles/'+ this.mobile + '/count/'(手机去重)
]