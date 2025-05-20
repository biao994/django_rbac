from rest_framework.permissions import BasePermission
from django.conf import settings
from .utils import PermissionCache

class RBACPermission(BasePermission):
    """
    RBAC权限控制类
    实现基于角色的访问控制，检查用户是否有访问资源的权限
    """
    def has_permission(self, request, view):
        # 1. 检查白名单
        if self._is_whitelist_path(request.path_info):
            return True
        
        # 2. 检查超级管理员
        if request.user.is_superuser:
            return True

        # 3. 获取权限标识
        permission_codename = self._get_permission_codename(request)

        # 4. 获取用户权限并检查
        user_permissions = PermissionCache.get_user_permissions(request.user.id)
        return permission_codename in user_permissions
    
    def _is_whitelist_path(self, path):
        """检查路径是否在白名单中"""
        return any(path.startswith(p) for p in settings.PERMISSION_WHITELIST)
    
    def _get_permission_codename(self, request):
        """
        生成权限标识
        格式为：{method}:{path}，例如：get:/api/rbac/permissions/
        """
        method = request.method.lower()
        path = request.path_info
        return f"{method}:{path}"