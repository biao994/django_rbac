# Django RBAC 权限管理系统

<div align="center">

![Django](https://img.shields.io/badge/Django-3.2-green)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![REST](https://img.shields.io/badge/REST-API-orange)
![Redis](https://img.shields.io/badge/Redis-Cache-red)

</div>

这是一个基于Django和Django REST framework实现的RBAC（基于角色的访问控制）权限管理系统。该系统提供了完整的用户认证、权限管理和角色管理功能。

> 📝 本项目有详细的开发教程博客，欢迎阅读：[Django RBAC权限管理系统开发教程](https://blog.csdn.net/weixin_46253270/category_12960723.html?spm=1001.2014.3001.5482)

## ✨ 项目亮点

- 🔐 基于JWT的认证系统，安全可靠
- 🚀 使用Redis缓存权限数据，性能优异
- 📦 模块化设计，易于扩展
- 🔄 完整的RESTful API接口
- 🛡️ 细粒度的权限控制
- 📝 详细的开发文档和教程

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Redis 6.0+
- Django 3.2
- Django REST framework 3.12.4

### 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd django_rbac
```

2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建超级用户
```bash
python manage.py createsuperuser
```

5. 运行开发服务器
```bash
python manage.py runserver
```

## 📚 项目结构

```
django_rbac/
├── django_rbac/          # 项目配置目录
│   ├── settings.py      # 项目设置
│   ├── urls.py         # URL配置
│   └── wsgi.py         # WSGI配置
├── users/               # 用户管理应用
│   ├── models.py       # 用户模型
│   ├── views.py        # 视图函数
│   └── serializers.py  # 序列化器
├── rbac/               # RBAC权限管理应用
│   ├── models.py       # 权限模型
│   ├── views.py        # 视图函数
│   └── permissions.py  # 权限类
└── manage.py           # Django管理脚本
```

## 🔧 配置说明

### 1. 数据库配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Redis配置
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 3. JWT配置
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

## 📡 API接口

### 认证相关
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/auth/login/` | POST | 用户登录 |
| `/api/auth/register/` | POST | 用户注册 |
| `/api/auth/refresh/` | POST | 刷新Token |

### 用户管理
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/users/` | GET | 获取用户列表 |
| `/api/users/{id}/` | GET | 获取用户详情 |
| `/api/users/{id}/` | PUT | 更新用户信息 |
| `/api/users/{id}/` | DELETE | 删除用户 |

### 角色管理
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/roles/` | GET | 获取角色列表 |
| `/api/roles/` | POST | 创建角色 |
| `/api/roles/{id}/` | GET | 获取角色详情 |
| `/api/roles/{id}/` | PUT | 更新角色 |
| `/api/roles/{id}/` | DELETE | 删除角色 |

### 权限管理
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/permissions/` | GET | 获取权限列表 |
| `/api/permissions/` | POST | 创建权限 |
| `/api/permissions/{id}/` | GET | 获取权限详情 |
| `/api/permissions/{id}/` | PUT | 更新权限 |
| `/api/permissions/{id}/` | DELETE | 删除权限 |

## 🔒 权限白名单

以下接口无需认证即可访问：
- `/api/auth/login/`
- `/api/auth/register/`
- `/api/auth/refresh/`

## 🛠️ 开发说明

### 1. 代码规范
- 遵循PEP 8编码规范
- 使用Black进行代码格式化

### 2. 测试
```bash
# 运行测试
python manage.py test

# 运行测试并显示覆盖率报告
coverage run manage.py test
coverage report
```


## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

