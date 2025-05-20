from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'roles', views.RoleViewSet, basename='role')

app_name = 'rbac'

urlpatterns = [
    path('rbac/', include(router.urls)),
] 




