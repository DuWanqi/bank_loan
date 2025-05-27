from django.db import models

# Create your models here.
# loan/models.py
from django.db import models
from django.contrib.auth.models import User  # 关联用户模型
from django.conf import settings

# class Loan(models.Model):
#     # 基础字段
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="申请人")
#     amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="贷款金额")
#     purpose = models.CharField(max_length=200, verbose_name="贷款用途")
#     status_choices = [
#         ('pending', '待审核'),
#         ('approved', '已批准'),
#         ('rejected', '已拒绝'),
#     ]
#     status = models.CharField(max_length=10, choices=status_choices, default='pending', verbose_name="状态")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")

#     def __str__(self):
#         return f"{self.user.username}的贷款申请（{self.amount}元）"

class Loan(models.Model):
    # 关联申请人（使用 settings.AUTH_USER_MODEL 动态引用）
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,  # 用户删除时级联删除贷款记录
        related_name="loans_as_user"  # 反向查询名称：用户作为借款人的贷款
    )
    
    # 贷款金额（精确到小数点后两位）
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="贷款金额"
    )

    term = models.PositiveSmallIntegerField(  # 新增term字段
        verbose_name="贷款期限（月）",
        choices=[(6, '6个月'), (12, '12个月'),(24, '24个月')],
        null=False 
    )
    
    # 贷款用途（限制最大长度）
    purpose = models.CharField(
        max_length=200, 
        verbose_name="贷款用途"
    )
    
    # 申请状态（有限选项）
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="状态"
    )
    
    # 自动记录申请时间
    created_at = models.DateTimeField(
        auto_now_add=True,  # 仅在创建时自动设置时间
        verbose_name="申请时间"
    )

    def __str__(self):
        return f"{self.user.phone}的贷款申请（{self.amount}元）"
    
    # #审批外键
    # approver = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,  # 动态引用当前用户模型
    #     on_delete=models.CASCADE,
    #     related_name="loans_as_approver"  # 反向查询名称：用户作为审批人的贷款
    # )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  # 允许表单不填
        related_name="approved_loans"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True  # 临时允许空值
    )