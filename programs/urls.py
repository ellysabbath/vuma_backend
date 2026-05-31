from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProgramList.as_view(), name='program-list'),
    path('<int:id>/', views.ProgramDetail.as_view(), name='program-detail'),
]