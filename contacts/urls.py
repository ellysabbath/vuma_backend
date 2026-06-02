from django.urls import path
from . import views

urlpatterns = [
    path('contact/', views.ContactMessageList.as_view(), name='contact-list'),
    path('contact/<int:id>/', views.ContactMessageDetail.as_view(), name='contact-detail'),
    path('contact/<int:id>/reply/', views.ContactMessageReplyView.as_view(), name='contact-reply'),
]