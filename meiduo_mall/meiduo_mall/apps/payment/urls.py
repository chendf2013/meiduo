from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from . import views

urlpatterns = [

    # 生成alipay登录网址
    url(r"^orders/(?P<order_id>\d+)/payment/$",views.GenerateUrlView.as_view()),
    # 后端保存订单
    url(r"payment/status/$",views.OverRideOrederStatusView.as_view()),
]
