from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    # 添加到购物车
    url(r'^cart/$', views.CartView.as_view()),

]

