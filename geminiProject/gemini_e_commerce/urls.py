from django.urls import path,include
from .views import *


urlpatterns = [
    path('chat/',GeminiChatView.as_view(),name='product-list'),
]