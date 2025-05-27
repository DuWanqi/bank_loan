# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import User

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'phone', 'role', 'is_staff')
#     search_fields = ('phone', 'username')
#     list_filter = ('role',)

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from .models import User
from .models import UserProfile

class ActiveUserFilter(admin.SimpleListFilter):
    title = '活跃状态'
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('30d', '近30天活跃'),
            ('90d', '近90天活跃')
        )

    def queryset(self, request, queryset):
        if self.value() == '30d':
            return queryset.filter(last_login__gte=timezone.now()-timedelta(days=30))
        if self.value() == '90d':
            return queryset.filter(last_login__gte=timezone.now()-timedelta(days=90))


    
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = '扩展资料'
    fields = ('avatar', 'phone')  # 根据实际模型字段调整
    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'phone', 'role', 'staff_status')
    search_fields = ('username__icontains', 'phone__exact', 'profile__email', 'groups__name')
    list_filter = ('role', ('date_joined', admin.DateFieldListFilter), ActiveUserFilter)

    def staff_status(self, obj):
        color = 'green' if obj.is_staff else 'red'
        return format_html('<span style="color:{};">{}</span>', color, '管理员' if obj.is_staff else '普通用户')
    staff_status.short_description = '权限状态'
    staff_status.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(role=request.user.role)
        return qs
