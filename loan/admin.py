# from django.contrib import admin

# # Register your models here.
# from django.contrib import admin
# from .models import Loan

# @admin.register(Loan)
# class LoanAdmin(admin.ModelAdmin):
#     list_display = ('user', 'amount', 'status', 'created_at')
#     # raw_id_fields = ('user',)  # 优化外键选择
#     list_display_links = ('user',)  # 点击用户名进入编辑页
    
#     def formatted_status(self, obj):
#         return f"【{obj.status}】"  # 自定义字段显示逻辑
#     formatted_status.short_description = '贷款状态'


# 新增代码部分
from django.contrib import admin
from django.http import HttpResponse
import xlwt
from datetime import datetime
from django.utils.html import format_html
from .models import Loan
from django.contrib.contenttypes.models import ContentType  # 修复 ContentType 报错
from django.contrib.admin.models import CHANGE, ADDITION  # 导入操作类型常量

def export_selected_loans(modeladmin, request, queryset):
    # 1. 创建响应对象并设置文件名
    response = HttpResponse(content_type='application/ms-excel')
    filename = f"loans_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xls"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 2. 创建 Excel 工作簿和表
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Loans')

    # 3. 定义表头（根据 Loan 模型字段调整）
    headers = ['用户', '金额', '状态', '创建时间']
    for col, header in enumerate(headers):
        sheet.write(0, col, header)

    # 4. 写入数据行
    for row, loan in enumerate(queryset, start=1):
        sheet.write(row, 0, str(loan.user))
        sheet.write(row, 1, loan.amount)
        sheet.write(row, 2, loan.status)
        sheet.write(row, 3, loan.created_at.strftime('%Y-%m-%d %H:%M'))

    wb.save(response)
    return response

export_selected_loans.short_description = "导出选中贷款到 Excel"

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    actions = [export_selected_loans]
    list_display = ('user', 'amount', 'formatted_status', 'status', 'created_at', 'approver')
    list_filter = ('status', ('created_at', admin.DateFieldListFilter))
    search_fields = ('user__username', 'amount')
    list_editable = ('status',)

    def formatted_status(self, obj):
        colors = {'approved': 'green', 'rejected': 'red', 'pending': 'orange'}
        return format_html(
            '<span style="color:{};">【{}】</span>',
            colors.get(obj.status, 'black'),
            obj.status.upper()
        )
    formatted_status.short_description = '贷款状态'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(approver=request.user)
        return qs

    def has_export_permission(self, request):
        return request.user.groups.filter(name='财务组').exists()
    
    def save_model(self, request, obj, form, change):
        # 记录变更前数据
        if change:
            original_obj = self.model.objects.get(pk=obj.pk)
            changes = self.compare_objects(original_obj, obj)
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE if change else ADDITION,
                change_message=changes
            )
        super().save_model(request, obj, form, change)
        
    def compare_objects(self, old, new):
        """对比新旧对象字段差异"""
        return {
            'changed_fields': [f.name for f in old._meta.fields if getattr(old, f.name) != getattr(new, f.name)]
        }

# 管理员日志
from django.contrib import admin
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    list_filter = ['action_time', 'user', 'content_type']
    readonly_fields = ['action_time', 'user', 'change_message']
    search_fields = ['object_repr', 'user__username']

    def has_add_permission(self, request):
        return False  # 禁止手动添加日志
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user=request.user)  # 仅显示当前用户的操作[9](@ref)
        return qs

    def operation_detail(self, obj):
        return obj.change_message
    operation_detail.short_description = '变更详情'  # 自定义列名[8](@ref)