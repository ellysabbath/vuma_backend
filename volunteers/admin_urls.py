from django.urls import path
from . import views

urlpatterns = [
    path('', views.VolunteerList.as_view(), name='volunteer-list'),
    path('<int:id>/', views.VolunteerDetail.as_view(), name='volunteer-detail'),
]