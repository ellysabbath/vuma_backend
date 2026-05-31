from django.urls import path
from . import admin_apis

urlpatterns = [
    path('', admin_apis.AdminUserList.as_view(), name='admin-user-list'),
    path('<int:id>/', admin_apis.AdminUserDetail.as_view(), name='admin-user-detail'),
]