from django.urls import path
from . import views  # 导入当前应用的视图

app_name = 'loan'
# 贷款模块路由配置
urlpatterns = [
    path('apply/', views.loan_apply, name='loan_apply'),      # 贷款申请
    path('status/<int:loan_id>/', views.loan_status, name='status'),  # 贷款状态查询
    # path('approve/<int:loan_id>/', views.loan_approve, name='approve'),
    path('admin/approve/<int:loan_id>/', views.approve_loan, name='approve_loan'),
    path('admin/pending/', views.admin_pending_loans, name='admin_pending_loans'),
]