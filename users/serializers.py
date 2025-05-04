from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器，用于处理用户注册时的数据验证和用户创建"""
    
    # 定义password字段的序列化规则
    password = serializers.CharField(
        write_only=True,  # 只用于写入
        required=True,    # 必填字段
        validators=[validate_password]  # 使用Django内置的密码验证器验证密码强度
    )
    
    # 定义password2（确认密码）字段
    password2 = serializers.CharField(
        write_only=True,  # 只用于写入
        required=True     # 必填字段
    )
    
    # 定义mobile字段
    mobile = serializers.CharField(
        required=True,    # 手机号为必填字段
        validators=[
            UniqueValidator(queryset=User.objects.all())  # 确保手机号在系统中是唯一的
        ]
    )

    class Meta:
        model = User  # 指定这个序列化器关联的模型
        fields = ('username', 'password', 'password2', 'mobile')  # 指定要序列化/反序列化的字段

    def validate(self, attrs):
        """
        全局验证方法，用于验证多个字段之间的关系
        attrs: 包含所有字段值的字典
        """
        # 验证两次输入的密码是否一致
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs

    def create(self, validated_data):
        """
        创建用户的方法
        validated_data: 经过验证的数据
        """
        # 删除validated_data中的password2字段，因为User模型中没有这个字段
        validated_data.pop('password2')
        # 使用create_user方法创建用户，这个方法会自动加密密码
        user = User.objects.create_user(**validated_data)
        return user

class UserDetailSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'roles')
        read_only_fields = ('roles',) # 角色字段设为只读，防止通过API直接修改用户角色

