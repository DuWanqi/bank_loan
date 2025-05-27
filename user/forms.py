# user/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User  # 导入自定义用户模型

class UserRegistrationForm(UserCreationForm):
    # 扩展字段：手机号输入（添加前端提示）
    phone = forms.CharField(
        label="手机号",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入11位手机号'
        }),
        help_text="必须为有效的中国大陆手机号"
    )

    class Meta(UserCreationForm.Meta):
        """
        继承自 Django 原生 UserCreationForm 的 Meta 类
        作用：关联模型 & 定义表单字段
        """
        model = User  # 绑定到你的自定义用户模型
        fields = ("phone", "password1", "password2")  # 显示字段顺序

    def clean_phone(self):
        """
        自定义手机号验证逻辑
        Django 表单系统会自动调用 clean_<fieldname> 方法
        """
        phone = self.cleaned_data.get('phone')  # 获取清洗后的数据
        
        # 格式验证
        if not phone.isdigit() or len(phone) != 11:
            raise ValidationError("手机号必须为11位纯数字", code='invalid_phone_format')
            
        # 唯一性验证
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("该手机号已被注册", code='phone_already_exists')
            
        return phone  # 必须返回验证通过的值

    def save(self, commit=True):
        """
        重写保存方法以添加默认角色
        """
        user = super().save(commit=False)  # 先不提交到数据库
        user.role = 'customer'  # 设置默认角色（根据你的模型定义）
        if commit:
            user.save()  # 保存到数据库
            self.save_m2m()  # 如果有多对多字段需要保存
        return user