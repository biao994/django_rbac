from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Permission, Role
from .utils import PermissionCache
from .serializers import PermissionSerializer, RoleSerializer


class PermissionViewSet(viewsets.ModelViewSet):
    """
    权限管理视图集
    提供权限的增删改查，并在权限变更时自动清除缓存
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def perform_create(self, serializer):
        """创建权限后清除所有用户的权限缓存"""
        serializer.save()
        PermissionCache.clear_user_permissions()

    def perform_update(self, serializer):
        """更新权限后清除所有用户的权限缓存"""
        serializer.save()
        PermissionCache.clear_user_permissions()

    def perform_destroy(self, instance):
        """删除权限后清除所有用户的权限缓存"""
        instance.delete()
        PermissionCache.clear_user_permissions()

class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图集
    提供角色的增删改查，并在角色变更时自动清除缓存
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        """创建角色后清除所有用户的权限缓存"""
        serializer.save()
        PermissionCache.clear_user_permissions()

    def perform_update(self, serializer):
        """更新角色后清除所有用户的权限缓存"""
        serializer.save()
        PermissionCache.clear_user_permissions()

    def perform_destroy(self, instance):
        """删除角色后清除所有用户的权限缓存"""
        instance.delete()
        PermissionCache.clear_user_permissions()
        
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """
        为角色分配权限
        """
        role = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        # 获取权限对象
        permissions = Permission.objects.filter(id__in=permission_ids)
        
        # 更新角色的权限
        role.permissions.set(permissions)
        
        PermissionCache.clear_user_permissions()
        
        return Response({
            "message": "权限分配成功",
            "role": RoleSerializer(role).data
        })
        
        
