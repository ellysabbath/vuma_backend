from django.urls import path
from . import admin_apis

urlpatterns = [
    path('', admin_apis.AdminPartnerList.as_view(), name='admin-partner-list'),
    path('<int:id>/', admin_apis.AdminPartnerDetail.as_view(), name='admin-partner-detail'),
]