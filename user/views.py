from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django_ratelimit.decorators import ratelimit
from django.contrib import messages  # 引入消息框架
# @ratelimit(key='post:phone', rate='5/m')  # 同一手机号每分钟最多5次尝试

# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')  # 跳转到登录页
#     else:
#         form = UserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})

# 函数视图正确示例（下划线命名）
from django.template import TemplateDoesNotExist
import os
def login_view(request):
    try:
        return render(request, 'user/login.html')
    except TemplateDoesNotExist:
        print("致命错误：模板路径验证失败！请检查以下路径是否存在：")
        print("当前项目路径:", os.path.dirname(__file__))
        print("预期模板路径:", os.path.join(os.path.dirname(__file__), 'templates/user/login.html'))
        raise

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
@login_required

def profile(request):
    """用户资料页（自动获取当前用户的Profile）"""
    user_profile = request.user.userprofile  # 通过反向关联直接访问[4](@ref)
    return render(request, 'user/profile.html', {'profile': user_profile})

# user/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login  # 核心模块引用
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm  # 导入自定义注册表单
from django.contrib.auth import get_user_model
User = get_user_model()  # 自动关联 settings.AUTH_USER_MODEL

# def register_view(request):
#     """
#     用户注册视图
#     流程：GET请求展示表单 → POST请求验证 → 保存用户 → 自动登录 → 重定向
#     """
#     # 处理 POST 请求（表单提交）
#     if request.method == 'POST':
#         # 将请求数据绑定到表单实例
#         form = UserRegistrationForm(request.POST)  
        
#         # 表单验证（自动触发 clean_phone 和密码验证）
#         if form.is_valid():  
#             # 保存用户（commit=False 允许添加额外字段）
#             user = form.save(commit=False)  
            
#             # --- 关键角色分配 ---
#             user.role = 'customer'  # 按业务规则分配默认角色（D4阶段核心需求）
            
#             # --- 安全存储密码 ---
#             # 无需手动操作！form.save() 已通过 UserCreationForm 自动调用 set_password()
            
#             # 提交到数据库
#             user.save()  
            
#             # --- 自动登录 ---
#             login(request, user)  # 调用Django Auth模块的login方法创建会话
            
#             # 重定向到D5阶段定义的贷款申请页（根据学习计划表衔接）
#             return redirect('loan_apply')  
    
#     # 处理 GET 请求（展示空表单）或验证失败
#     else:
#         form = UserRegistrationForm()  # 创建空表单实例
    
#     # 渲染模板（含错误提示）
#     return render(request, 'registration/register.html', {'form': form}) 
# def register_view(request):
#     if request.method == 'POST':
#         # 手动提取数据（替代原表单绑定）
#         phone = request.POST.get('phone')
#         password = request.POST.get('password')
        
#         # --- 手机号格式验证（原代码依赖表单，无法自定义错误提示）---
#         if len(phone) != 11 or not phone.isdigit():
#             return render(request, 'user/register.html', {'error': '手机号必须为11位数字'})
        
#         # --- 手机号唯一性验证（原代码无此逻辑）---
#         if User.objects.filter(phone=phone).exists():
#             return render(request, 'user/register.html', {'error': '该手机号已注册'})
        
#         # --- 密码一致性验证（原代码依赖表单字段）---
#         if password != request.POST.get('confirm_password'):
#             return render(request, 'user/register.html', {'error': '两次输入密码不一致'})
        
#         # --- 安全创建用户（显式加密密码）---
#         user = User.objects.create_user(  #  使用 create_user 自动加密
#             phone=phone,
#             password=password,
#             role='customer'  # 直接分配角色（避免中间变量）
#         )
        
#         # 自动登录（保持原有逻辑）
#         login(request, user)  
#         return redirect('loan_apply')
    
#     # GET 请求渲染模板（路径修正）
#     return render(request, 'user/register.html')

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # --- 验证逻辑 ---
        error = None
        if len(phone) != 11 or not phone.isdigit():
            error = '手机号必须为11位数字'
        elif User.objects.filter(phone=phone).exists():
            error = '该手机号已注册'
        elif password != confirm_password:
            error = '两次输入密码不一致'

        if error:
            #  关键：使用重定向 + 消息框架传递错误（避免重复提交）
            messages.error(request, error)
            return redirect('register')  # 路由名需在 urls.py 中定义

        # --- 创建用户并登录 ---
        user = User.objects.create_user(phone=phone, password=password, role='customer')
        user.backend = 'user.backends.PhoneAuthBackend'
        login(request, user)
        return redirect("loan:loan_apply")
    
    # GET 请求：显示注册页并渲染消息
    return render(request, 'user/register.html')