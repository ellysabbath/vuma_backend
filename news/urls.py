from django.urls import path
from . import views

urlpatterns = [
    path('', views.NewsList.as_view(), name='news-list'),
    path('<int:id>/', views.NewsDetail.as_view(), name='news-detail'),
    path('<int:id>/like/', views.NewsLikeView.as_view(), name='news-like'),
]