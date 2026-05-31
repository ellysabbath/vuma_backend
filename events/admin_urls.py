from django.urls import path
from . import views

urlpatterns = [
    path('', views.EventList.as_view(), name='event-list'),
    path('<int:id>/', views.EventDetail.as_view(), name='event-detail'),
    path('<int:id>/register/', views.EventRegisterView.as_view(), name='event-register'),
]