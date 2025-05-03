from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile = models.CharField("手机号", max_length=11,unique=True)
    roles = models.ManyToManyField('rbac.Role', verbose_name="所属角色",blank=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str(self):
        return  self.username                      
