from django.contrib.auth.models import AbstractUser
from django.db import models

# class User(AbstractUser):
#     # 完全移除默认的username字段
#     username = None
#     # 手机号作为唯一登录标识
#     phone = models.CharField('手机号', max_length=20, unique=True)
#     # 头像字段（可选）
#     avatar = models.ImageField('头像', upload_to='avatar/', blank=True)
    
#     # 设置手机号为认证字段
#     USERNAME_FIELD = 'phone'
#     # 创建超级用户时必须填写的字段（此处设为email）
#     REQUIRED_FIELDS = ['email']
    
#     class Meta:
#         db_table = 'tb_user'  # 自定义表名
#         verbose_name = '用户管理'  # 后台显示名称

# class User(AbstractUser):
#     # 关键修改点1：修复username唯一性约束
#     username = models.CharField(
#         max_length=150,
#         unique=True,  # 必须添加的唯一性约束
#         verbose_name="用户名"
#     )
    
#     # 角色字段（保持原逻辑）
#     ROLE_CHOICES = [
#         ('customer', '客户'),
#         ('staff', '员工'),
#         ('admin', '管理员'),
#     ]
#     role = models.CharField(
#         max_length=10, 
#         choices=ROLE_CHOICES, 
#         default='customer',
#         verbose_name="用户角色"
#     )
    
#     # 关键修改点2：将phone设为唯一标识符（替代username）
#     phone = models.CharField(
#         max_length=20, 
#         unique=True,  # 唯一性约束
#         verbose_name="手机号"
#     )
    
#     # 头像字段（保持原逻辑）
#     avatar = models.ImageField(
#         upload_to='avatars/', 
#         blank=True, 
#         verbose_name="头像"
#     )

#     # 关键修改点3：覆盖groups和user_permissions字段，避免反向访问器冲突
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='custom_user_groups',  # 自定义反向名称
#         blank=True,
#         verbose_name='用户组',
#         help_text='用户所属的组'
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='custom_user_permissions',  # 自定义反向名称
#         blank=True,
#         verbose_name='用户权限',
#         help_text='用户特定权限'
#     )

#     # 关键修改点4：将登录标识符改为手机号
#     USERNAME_FIELD = 'phone'  # 使用手机号作为唯一登录凭证
#     REQUIRED_FIELDS = ['username']  # 必须包含username，但实际注册时可不使用

from django.contrib.auth.models import BaseUserManager

class PhoneUserManager(BaseUserManager):
    """完全适配手机号体系的管理器"""
    
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('必须填写手机号')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        # 强制激活超级用户权限[2,7](@ref)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)
    
class User(AbstractUser):
    username = None
    # username = models.CharField(
    #     max_length=150,
    #     null=True,
    #     blank=True,
    #     default=None,
    #     unique=False  # 取消唯一性约束
    # )
    
    # 手机号（主登录标识）
    phone = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="手机号"
    )
    
    # 用户角色
    ROLE_CHOICES = [
        ('customer', '客户'),
        ('staff', '员工'),
        ('admin', '管理员'),
    ]
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='customer',
        verbose_name="用户角色"
    )
    
    # 权限系统兼容字段
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='%(app_label)s_%(class)s_groups',
        blank=True,
        verbose_name='用户组'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='%(app_label)s_%(class)s_permissions',
        blank=True,
        verbose_name='用户权限'
    )
    
    # 认证系统标识配置
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = PhoneUserManager()  # 替换默认管理器[4,7](@ref)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 一对一关联核心用户模型[2,4](@ref)
    phone = models.CharField(max_length=20, blank=True)         # 扩展手机号字段
    avatar = models.ImageField(upload_to='avatars/', blank=True) # 扩展头像字段
    created_at = models.DateTimeField(auto_now_add=True)         # 用户注册时间

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
