from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# 认证相关的URL模式
auth_patterns = [
    path('register/', views.register, name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

app_name = 'users'

urlpatterns = [
    path('auth/', include(auth_patterns)),  # 将认证相关的URL归为一组
]