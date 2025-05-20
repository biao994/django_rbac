from django.core.cache import cache
from django.conf import settings
from .models import Permission
from django.contrib.auth import get_user_model

User = get_user_model()

class PermissionCache:
    """
    权限缓存工具类
    用于管理用户权限的缓存操作，包括获取和清除缓存
    """

    @staticmethod
    def get_user_permissions(user_id):
        """
        获取用户的权限列表
        优先从缓存中获取，如果缓存不存在则从数据库查询并缓存
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 用户权限列表，包含权限的codename
        """
        # 构建缓存键
        cache_key = f"user_permissions_{user_id}"
        
        try:
            # 尝试从缓存获取权限
            permissions = cache.get(cache_key)
            
            # 如果缓存中没有，从数据库查询
            if permissions is None:
                permissions = PermissionCache._get_permissions_from_db(user_id)
                # 将查询结果存入缓存
                try:
                    cache.set(cache_key, list(permissions), 
                             settings.PERMISSION_CACHE_TIMEOUT)
                except Exception:
                    # 如果缓存操作失败，忽略错误继续执行
                    pass
                
            return permissions
        except Exception:
            # 发生异常时从数据库查询
            return PermissionCache._get_permissions_from_db(user_id)
    
    @staticmethod
    def _get_permissions_from_db(user_id):
        """从数据库直接查询用户权限"""
        try:
            # 方式一：使用查询集
            user = User.objects.get(id=user_id)
            role_ids = user.roles.values_list('id', flat=True)
            permissions = Permission.objects.filter(
                role__in=role_ids
            ).distinct().values_list('codename', flat=True)
            return list(permissions)
        except Exception:
            return []

    @staticmethod
    def clear_user_permissions(user_id=None):
        """
        清除用户权限缓存
        可以清除单个用户的缓存，也可以清除所有用户的缓存
        
        Args:
            user_id: 可选参数，指定要清除缓存的用户ID
                    如果不传，则清除所有用户的缓存
        """
        try:
            if user_id:
                # 清除指定用户的缓存
                cache.delete(f"user_permissions_{user_id}")
            else:
                # 清除所有用户的缓存（使用通配符）
                cache.delete_pattern("user_permissions_*")
        except Exception:
            # 如果清除缓存失败，忽略错误
            pass