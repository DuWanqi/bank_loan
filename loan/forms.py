# loan/forms.py
from django import forms
from .models import Loan

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['term', 'amount', 'purpose']  # 假设Loan模型包含这些字段[6,7](@ref)
        
        # 自定义字段标签和错误提示（网页5、网页7）
        labels = {
            'term': '贷款期限（月）',
            'amount': '贷款金额',
            'purpose': '贷款用途'
        }
        error_messages = {
            'term': {
                'required': '请选择贷款期限',
                'invalid_choice': '期限必须为6/12/24个月'
            },
            'amount': {
                'required': '请输入贷款金额',
                'invalid': '请输入有效数字'
            }
        }

    # 添加自定义验证（网页7、网页10）
    def clean_term(self):
        term = self.cleaned_data.get('term')
        if term not in [6, 12, 24]:
            raise forms.ValidationError("期限必须为6/12/24个月")
        return term

    # 覆盖默认的字段控件（网页9、网页10）
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['term'].widget = forms.Select(
            choices=[(6, '6个月'), (12, '12个月'), (24, '24个月')],
            attrs={'class': 'form-select'}
        )
        self.fields['amount'].widget = forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '请输入金额（单位：元）'
            }
        )
        self.fields['purpose'].widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '请简要说明贷款用途'
            }
        )