from django.urls import path
from . import views

urlpatterns = [
    # Donation endpoints
    path('donations/', views.DonationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='donation-list'),
    
    path('donations/<int:pk>/', views.DonationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='donation-detail'),
    
    # Custom actions
    path('donations/<int:pk>/confirm_payment/', views.DonationViewSet.as_view({'post': 'confirm_payment'}), name='donation-confirm-payment'),
    path('donations/status/', views.DonationViewSet.as_view({'post': 'update_status'}), name='donation-status'),
    path('donations/stats/', views.DonationViewSet.as_view({'get': 'stats'}), name='donation-stats'),
    path('donations/by-email/', views.DonationViewSet.as_view({'get': 'get_by_email'}), name='donations-by-email'),
    path('donations/by-reference/', views.DonationViewSet.as_view({'get': 'get_by_reference'}), name='donations-by-reference'),
    
    # Donation logs (admin only)
    path('donation-logs/', views.DonationLogViewSet.as_view({'get': 'list'}), name='donationlog-list'),
    path('donation-logs/<int:pk>/', views.DonationLogViewSet.as_view({'get': 'retrieve'}), name='donationlog-detail'),
]