"""
URL configuration for bank_loan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView  # 新增导入

urlpatterns = [
    path('admin/', admin.site.urls),
    # 包含用户模块路由（命名空间可选）
    path('user/', include(('user.urls', 'user'), namespace='user')),
    # 包含贷款模块路由
    path('loan/', include('loan.urls')),

    path('', RedirectView.as_view(url='/loan/apply/')),
]
