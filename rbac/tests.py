from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.conf import settings
from .models import Role, Permission
from .utils import PermissionCache

User = get_user_model()
print("测试文件已加载")
class RBACPermissionTest(TestCase):
    def setUp(self):
        """测试数据初始化：创建用户、角色和权限"""
        # 清理顺序：先缓存后数据库
        # 1. 清理所有用户权限缓存（防止旧缓存影响测试）
        PermissionCache.clear_user_permissions()  # 清空redis中所有user_permissions_*键
        
        # 2. 清理数据库（保证测试环境干净）
        Permission.objects.all().delete()  # 删除所有权限记录
        Role.objects.all().delete()        # 删除所有角色记录
        User.objects.all().delete()        # 删除所有用户记录
        
        # 创建测试用户
        self.user = User.objects.create_user(
            username='test_user',
            password='test123456',
            mobile='13800000001',
            is_superuser=False  # 明确设置为非超级用户
        )

        self.admin = User.objects.create_user(
            username='admin_user',
            password='admin123456',
            mobile='13800000002', 
            is_superuser=True
        )

        # 创建角色
        self.user_role = Role.objects.create(name='普通用户')
        self.admin_role = Role.objects.create(name='管理员')

        # 创建权限
        self.view_permission = Permission.objects.create(
            codename='get:/api/rbac/permissions/',
            desc='查看权限列表'
        )
        self.create_permission = Permission.objects.create(
            codename='post:/api/rbac/permissions/',
            desc='创建权限'
        )

        # 分配角色给用户
        self.user.roles.add(self.user_role)
        self.admin.roles.add(self.admin_role)

        # 创建API客户端，并启用权限检查
        self.client = APIClient(enforce_csrf_checks=True)
        
        # 打印权限信息
        print(f"已创建用户: {self.user.username}, 超级用户: {self.user.is_superuser}")
        print(f"已创建权限: {self.view_permission.codename}")
        
        # 确保数据库中的权限情况
        print(f"数据库中的所有权限: {list(Permission.objects.values_list('codename', flat=True))}")
        print(f"用户角色: {list(self.user.roles.values_list('name', flat=True))}")
        print(f"角色权限: {list(self.user_role.permissions.values_list('codename', flat=True))}")

    def test_user_permissions(self):
        """
        测试权限判断逻辑：
        1. 未授权用户应该无法访问受保护资源
        2. 授权用户应该能够访问已获权限资源
        3. 授权用户不能访问未获权限资源
        """
        # 登录获取token
        response = self.client.post('/api/auth/login/', {
            'username': 'test_user',
            'password': 'test123456'
        })
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        
        # 测试未分配权限时访问（应该失败）
        print("\n--- 测试未分配权限时访问 ---")
        response = self.client.get('/api/rbac/permissions/')
        print(f"响应状态码: {response.status_code}")
        self.assertEqual(response.status_code, 403)

        # 分配权限
        print("\n--- 分配权限并测试 ---")
        self.user_role.permissions.add(self.view_permission)
        # 清除缓存以确保权限更新生效
        PermissionCache.clear_user_permissions(self.user.id)
        
        # 打印权限分配信息
        print(f"用户角色: {list(self.user.roles.values_list('name', flat=True))}")
        print(f"角色权限: {list(self.user_role.permissions.values_list('codename', flat=True))}")

        # 测试分配权限后访问（应该成功）
        response = self.client.get('/api/rbac/permissions/')
        print(f"响应状态码: {response.status_code}")
        self.assertEqual(response.status_code, 200)

        # 测试访问未授权资源（应该失败）
        print("\n--- 测试访问未授权资源 ---")
        response = self.client.post('/api/rbac/permissions/', {
            'codename':'test:permission',
            'desc':'测试权限'
        })
        print(f"响应状态码: {response.status_code}")
        self.assertEqual(response.status_code, 403)

    def test_admin_permissions(self):
        """
        测试管理员权限：
        1. 超级管理员应该能够访问所有资源，无需额外授权
        """
        # 登录获取token
        response = self.client.post('/api/auth/login/',{
            'username':'admin_user',
            'password':'admin123456'
        })
        print(f"登录响应: {response.data}")
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # 测试查看权限类别（应该成功）
        response = self.client.get('/api/rbac/permissions/')
        self.assertEqual(response.status_code, 200)

        # 测试拆解权限（应该成功）
        response = self.client.post('/api/rbac/permissions/',{
            'codename':'test:permission',
            'desc':'测试权限'
        })
        self.assertEqual(response.status_code, 201)
        
        # 验证权限确实被创建
        self.assertTrue(Permission.objects.filter(codename='test:permission').exists())

    def test_assign_permissions(self):
        """
        测试角色权限分配：
        1. 验证权限分配操作是否正确反映在数据库中
        2. 测试异常情况下的权限分配（不存在的权限ID等）
        3. 测试特殊场景（空权限列表、重复权限）
        """
        # 登录获取token
        response = self.client.post('/api/auth/login/',{
            'username':'admin_user',
            'password':'admin123456'
        })
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 测试新权限
        response = self.client.post('/api/rbac/permissions/',{
            'codename':'test:permission2',  # 使用不同的codename避免冲突
            'desc':'测试权限2'
        })
        new_permission_id  = response.data['id']

        # 测试分配权限
        response = self.client.post(
            f'/api/rbac/roles/{self.user_role.id}/assign_permissions/',
            {'permission_ids':[self.view_permission.id, new_permission_id]},
            format='json'  # 指定JSON格式，确保复杂数据结构正确传递
        )
        self.assertEqual(response.status_code, 200)

        # 验证权限分配结果已写入数据库
        self.assertEqual(set(self.user_role.permissions.values_list('id', flat=True)),
                         {self.view_permission.id, new_permission_id})
        
        # 测试普通用户分配权限（应该失败，验证权限控制）
        response = self.client.post('/api/auth/login/', {
            'username': 'test_user',
            'password': 'test123456'
        })
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')       
            
        response = self.client.post(f'/api/rbac/roles/{self.user_role.id}/assign_permissions/', {
            'permission_ids': [self.view_permission.id]
        })
        self.assertEqual(response.status_code, 403)

        # 测试边界情况，分配不存在的权限ID
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/rbac/roles/{self.user_role.id}/assign_permissions/', {
            'permission_ids': [99999]  # 不存在的权限ID
        })     
        self.assertEqual(response.status_code, 403)

        # 测试边界情况，分配空权限列表
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/rbac/roles/{self.user_role.id}/assign_permissions/', {
            'permission_ids': []
        })
        self.assertEqual(response.status_code, 403)

        # 测试边界情况，分配重复权限
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.post(f'/api/rbac/roles/{self.user_role.id}/assign_permissions/', {
            'permission_ids': [self.view_permission.id, self.view_permission.id]
        })
        self.assertEqual(response.status_code, 403)

    def test_permission_cache(self):
        """
        测试权限缓存机制：
        1. 缓存创建：首次获取权限时应创建缓存
        2. 缓存读取：再次获取权限时应从缓存读取
        3. 缓存更新：权限变更后清除缓存，再次获取应包含新权限
        4. 缓存删除：清除缓存后应从数据库重新加载
        5. 批量缓存清除：应能清除多个用户的缓存
        6. 缓存过期：设置短暂过期时间后，缓存应自动失效
        """
        # 登录获取token
        response = self.client.post('/api/auth/login/',{
            'username':'admin_user',
            'password':'admin123456'
        })
        token = response.data['data']['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # 1. 测试缓存创建
        # 分配权限给角色
        self.admin_role.permissions.add(self.view_permission)

        # 通过API请求触发缓存创建
        response = self.client.get('/api/rbac/permissions/')
        self.assertEqual(response.status_code, 200)

        # 验证缓存已创建并可以正确读取
        Permissions = PermissionCache.get_user_permissions(self.admin.id)
        self.assertIsNotNone(Permissions)
       
        # 2. 测试缓存更新
        # 创建新权限
        new_permission = Permission.objects.create(
            codename='test:permission3',
            desc='测试权限3'
        )
        # 分配新权限给角色
        self.admin_role.permissions.add(new_permission)
        
        # 确保view_permission也被分配
        self.admin_role.permissions.add(self.view_permission)
        
        # 清除缓存
        PermissionCache.clear_user_permissions(self.admin.id)
        
        # 获取更新后的权限（应包含新权限）
        updated_permissions = PermissionCache.get_user_permissions(self.admin.id)
        self.assertEqual(updated_permissions, ['get:/api/rbac/permissions/', 'test:permission3'])
        
        # 3. 测试权限删除
        # 先从数据库中移除权限
        self.admin_role.permissions.remove(self.view_permission)

        # 清除缓存
        PermissionCache.clear_user_permissions(self.admin.id)

        # 验证权限已被移除
        permissions = PermissionCache.get_user_permissions(self.admin.id)
        self.assertEqual(permissions, ['test:permission3'])  # 现在应该只有test:permission3
        
        # 4.测试批量缓存清除
        # 为多个用户分配权限并创建缓存
        self.user_role.permissions.add(self.view_permission)
        PermissionCache.get_user_permissions(self.user.id)
        PermissionCache.get_user_permissions(self.admin.id)

        # 清除所有用户缓存
        PermissionCache.clear_user_permissions()

        # 验证所有用户缓存已被清除并重新加载
        user_permissions = PermissionCache.get_user_permissions(self.user.id)
        admin_permissions = PermissionCache.get_user_permissions(self.admin.id)
        self.assertEqual(user_permissions, ['get:/api/rbac/permissions/'])
        self.assertEqual(admin_permissions, ['test:permission3'])

        # 5.测试缓存过期
        # 设置缓存过期时间为1秒
        original_permissions = settings.PERMISSION_CACHE_TIMEOUT
        settings.PERMISSION_CACHE_TIMEOUT = 1

        # 获取权限（创建缓存）
        PermissionCache.get_user_permissions(self.admin.id)

        # 验证缓存创建
        self.assertIsNotNone(PermissionCache.get_user_permissions(self.admin.id))

        # 等待缓存过期
        import time
        time.sleep(2)

        # 验证缓存已过期并重新加载
        permissions = PermissionCache.get_user_permissions(self.admin.id)
        self.assertEqual(permissions, ['test:permission3'])
        
        # 恢复原始缓存时间
        settings.PERMISSION_CACHE_TIMEOUT = original_permissions
        
    def test_permission_class_functions(self):
        """
        测试权限类特定功能：
        1. 白名单功能：白名单内的路径应无需权限即可访问
        2. 权限标识符生成：验证权限标识符生成逻辑正确性
        """
        # 测试白名单功能
        # 白名单路径应直接通过权限检查
        response = self.client.get('/api/auth/login/')
        self.assertNotEqual(response.status_code, 403)

        # 测试权限标识符生成
        from rbac.permissions import RBACPermission
        permission_check = RBACPermission()

        # 创建模拟请求
        from django.http import HttpRequest
        request = HttpRequest()
        request.method = 'GET'
        request.path_info = '/api/rbac/permissions/'

        # 生成权限标识符
        permission_codename = permission_check._get_permission_codename(request)
        self.assertEqual(permission_codename, 'get:/api/rbac/permissions/')
        
        


        

