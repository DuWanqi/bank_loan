from django.urls import path
from . import views  # 导入当前应用的视图
from .views import login_view
from user.views import register_view
app_name = 'user'
# 用户模块路由配置
urlpatterns = [
    # path('register/', views.register, name='register'),  # 用户注册
    path('register/', register_view, name='register'),
    path('login/', views.login_view, name='login'),      # 用户登录
    path('profile/', views.profile, name='profile'),     # 用户资料
]