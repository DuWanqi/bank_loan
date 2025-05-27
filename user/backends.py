from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()  # 获取当前激活的用户模型（您的 User 类）

class PhoneAuthBackend(ModelBackend):
    """
    自定义认证后端：手机号+密码登录
    （资源参考：网页2 - Django官方认证文档）
    """

    def authenticate(self, request, phone=None, password=None, **kwargs):
        # --- 原理1：Django 认证流程 ---
        # 1. 视图层调用 authenticate() 时传递登录参数
        # 2. 每个已注册的 backend 会按顺序尝试认证
        # 3. 第一个成功返回用户的 backend 生效

        try:
            # --- 原理2：多条件查询 ---
            # 使用 Q 对象支持手机号或用户名登录（兼容管理员后台）
            user = User.objects.get(Q(phone=phone) | Q(username=phone))
            
            # --- 原理3：密码验证 ---
            # check_password 会自动处理加密哈希验证
            if user.check_password(password):
                return user  # 认证成功返回用户对象
        except User.DoesNotExist:
            return None  # 认证失败
        except User.MultipleObjectsReturned:
            # 防止手机号与用户名重复导致冲突
            return User.objects.filter(phone=phone).first()

    def get_user(self, user_id):
        # --- 原理4：会话持久化 ---
        # 登录成功后，Django 通过此方法加载用户对象到请求中
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None