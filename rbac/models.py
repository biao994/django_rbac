from django.db import models

class Permission(models.Model):
    codename = models.CharField("权限别名", max_length=128, unique=True)
    desc = models.CharField("权限描述", max_length=128, blank=True)
    menu = models.CharField("关联菜单", max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = verbose_name

    def __str(self):
        return f"{self.codename} - {self.desc}"

class Role(models.Model):
    name = models.CharField("角色名称", max_length=128, unique=True)
    permissions = models.ManyToManyField(Permission, verbose_name="权限集合", blank=True)

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name