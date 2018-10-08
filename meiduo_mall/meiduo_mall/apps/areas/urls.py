from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from areas import views

router = DefaultRouter()
router.register(r"areas", views.AreaViewSet, base_name="areas")
router.register(r"addresses",views.AddressViewSet,base_name="addresses")

urlpatterns = [
    url(r"^", include(router.urls)),
]
