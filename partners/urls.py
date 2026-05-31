from django.urls import path
from . import views

urlpatterns = [
    path('', views.PartnerList.as_view(), name='partner-list'),
    path('<int:id>/', views.PartnerDetail.as_view(), name='partner-detail'),
    path('stats/', views.PartnerStatsView.as_view(), name='partner-stats'),
]