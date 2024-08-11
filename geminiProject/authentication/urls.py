from django.urls import path
from .views import *

urlpatterns = [
    path('register/',CreateUser.as_view(),name='register'),
    path('login/',CustomUserTokenObtainPairView.as_view(),name='login'),
    path('get_user/',GetUserDetails.as_view(),name='get_user'),
]