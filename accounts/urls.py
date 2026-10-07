from django.urls import path

from .views import login_page

urlpatterns = [
    path("login/", login_page, name="login-page"),
]
