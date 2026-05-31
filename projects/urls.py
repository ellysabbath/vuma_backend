from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectList.as_view(), name='project-list'),
    path('<int:id>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('stats/', views.ProjectStatsView.as_view(), name='project-stats'),
]