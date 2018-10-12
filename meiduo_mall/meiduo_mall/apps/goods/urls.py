from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    # 获取热销商品
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HotSKUListView.as_view()),
    # 获取商品列表
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),

]

router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')