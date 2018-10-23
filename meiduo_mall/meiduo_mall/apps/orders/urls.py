from django.conf.urls import url

from . import views

urlpatterns = [
    # 生成订单
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view()),
    # 提交订单
    url(r"^orders/$",views.SaveOrderView.as_view())
]
