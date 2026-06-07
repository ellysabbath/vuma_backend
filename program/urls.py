from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'prog', views.ProgramViewSet, basename='prog')
router.register(r'activity', views.ActivityViewSet, basename='activity')
router.register(r'explanation', views.ExplanationViewSet, basename='explanatio')

urlpatterns = [
    path('', include(router.urls)),
]

