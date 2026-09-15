from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    扩展 Django 内置用户表，增加角色和所属学院字段。
    role:
        admin   - 管理员（可查看所有项目、管理用户）
        teacher - 教师（可提交项目申报）
        expert  - 专家（可审核项目）
    """
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('teacher', '教师'),
        ('expert', '专家'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='teacher',
        verbose_name='角色'
    )
    college = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='所属学院'
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = '用户'
        verbose_name_plural = '用户管理'

    def __str__(self):
        return f'{self.username}（{self.get_role_display()}）'
