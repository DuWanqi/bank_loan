from django.shortcuts import render

# Create your views here.
# loan/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Loan  # 假设已创建贷款模型
from django.contrib.auth.decorators import login_required
from .forms import LoanApplicationForm  # 使用ModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required, user_passes_test

from django.shortcuts import get_object_or_404
from .forms import LoanApplicationForm  # 需创建表单类

@login_required
@user_passes_test(lambda u: u.role == 'customer', login_url='/permission_denied/')
# def loan_apply(request):
#     if request.method == 'POST':
#         form = LoanApplicationForm(request.POST)
#         if form.is_valid():
#             loan = form.save(commit=False)
#             loan.applicant = request.user
#             loan.status = 'pending'
#             loan.save()
#             return redirect('loan:status', loan_id=loan.id)
#     else:
#         form = LoanApplicationForm()
#     return render(request, 'loan/apply.html', {'form': form})
def loan_apply(request):
    if not request.user.is_authenticated:
        return redirect('user_register')
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            #  保存贷款申请数据并与用户关联
            # loan = form.save(commit=False)
            # loan.user = request.user
            # loan.save()
            # messages.success(request, '贷款申请已提交')
            loan = form.save(commit=False)
            loan = Loan(
            applicant=request.user,  # 关键点[8,9](@ref)
            amount=request.POST['amount'],
            purpose=request.POST['purpose']
        )
            loan.approver = None  # 明确设置为空
            loan.status = 'pending'
            loan.save()
            
            messages.success(request, '申请已提交，等待审批')
            return redirect('loan_status')  # 跳转到申请状态页
        else:
            messages.error(request, '请修正以下错误')
    else:
        form = LoanApplicationForm()  # 初始化空表单
    
    return render(request, 'loan/apply.html', {'form': form})

class LoanStatusView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loan/status.html'
    context_object_name = 'loan'

    def get_queryset(self):
        # 强制过滤当前用户数据
        return super().get_queryset().filter(applicant=self.request.user)

# @login_required
# @user_passes_test(lambda u: u.role == 'staff')
# def loan_approve(request, loan_id):
#     loan = get_object_or_404(Loan, id=loan_id)
#     if request.method == 'POST':
#         loan.status = 'approved' if 'approve' in request.POST else 'rejected'
#         loan.save()
#     return render(request, 'loan/approve.html', {'loan': loan})
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    if request.method == 'POST':
        # 绑定当前管理员为审批人，并更新状态
        loan.approver = request.user
        loan.status = 'approved'
        loan.save()
        messages.success(request, '贷款已批准')
        return redirect('admin_pending_loans')
    return render(request, 'loan/admin_approve.html', {'loan': loan})

def loan_status(request, loan_id):
    """贷款状态查询视图"""
    # 仅允许用户查看自己的贷款记录
    loan = get_object_or_404(Loan, id=loan_id, applicant=request.user)
    return render(request, 'loan/status.html', {'loan': loan})

@staff_member_required
def admin_pending_loans(request):
    loans = Loan.objects.filter(status='pending', approver__isnull=True)
    return render(request, 'loan/admin_pending.html', {'pending_loans': loans})