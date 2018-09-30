from django.conf.urls import url

from . import views

urlpatterns = [
    # url(r'^users/$', views.UserRegister.as_view()),
    url(r"qq/authorization/$",views.QQAuthURLView.as_view())
]
