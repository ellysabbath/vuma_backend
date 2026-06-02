from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'leaders', views.LeaderViewSet)
router.register(r'missions', views.ProjectViewSet)
router.register(r'testimonials', views.TestimonialViewSet)
router.register(r'blog-posts', views.BlogPostViewSet)
router.register(r'statistics', views.StatisticViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]