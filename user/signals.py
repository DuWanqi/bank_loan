# user/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """用户注册时自动创建关联的UserProfile"""
    if created:
        UserProfile.objects.create(user=instance)  # 创建一对一档案[2,4](@ref)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """用户信息更新时同步保存档案"""
    instance.userprofile.save()  # 通过反向关联保存[4](@ref)