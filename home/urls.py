# home/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('auth/signup', views.signup, name='signup'),
    path('auth/signin', views.signin, name='signin'),
    path('auth/signout', views.signout, name='signout'),
    path('auth/user', views.get_user, name='get_user'),
    path('auth/profile', views.update_profile, name='update_profile'),
    path('auth/update-password', views.update_password, name='update_password'),
    path('auth/reset-password', views.reset_password, name='reset_password'),
    path('auth/verify-email', views.verify_email, name='verify_email'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
