from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import ContactMessage
from .serializers import ContactMessageSerializer

class ContactMessageList(APIView):
    permission_classes = []  # No permission classes for public access
    
    def get(self, request):
        """Get all contact messages (for admin)"""
        messages = ContactMessage.objects.all()
        serializer = ContactMessageSerializer(messages, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Submit a new contact message"""
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            
            # Send email notifications
            self.send_notification_emails(message)
            
            return Response({
                'success': True,
                'message': 'Your message has been sent successfully. We will get back to you soon!',
                'data': ContactMessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_notification_emails(self, message):
        """Send email notifications to admin and auto-reply to user"""
        try:
            # 1. Send email to admin
            admin_subject = f"New Contact Message: {message.subject or 'No Subject'}"
            
            admin_html_message = render_to_string('emails/contact_admin_notification.html', {
                'name': message.name,
                'email': message.email,
                'subject': message.subject or 'No Subject',
                'message': message.message,
                'created_at': message.created_at.strftime('%B %d, %Y at %H:%M'),
                'admin_url': getattr(settings, 'SITE_URL', 'http://localhost:3000') + '/admin/contact'
            })
            
            admin_text_message = strip_tags(admin_html_message)
            
            # Send to admin email from settings
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@vuma.or.tz')
            
            admin_email_msg = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
                reply_to=[message.email]
            )
            admin_email_msg.attach_alternative(admin_html_message, "text/html")
            admin_email_msg.send(fail_silently=False)
            
            # 2. Send auto-reply to user
            user_subject = "Thank you for contacting VUMA Tanzania"
            
            user_html_message = render_to_string('emails/contact_user_autoreply.html', {
                'name': message.name,
                'message': message.message,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:3000')
            })
            
            user_text_message = strip_tags(user_html_message)
            
            user_email_msg = EmailMultiAlternatives(
                subject=user_subject,
                body=user_text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[message.email],
            )
            user_email_msg.attach_alternative(user_html_message, "text/html")
            user_email_msg.send(fail_silently=False)
            
            print(f"Sent contact notifications for message from {message.name}")
            
        except Exception as e:
            print(f"Error sending contact emails: {str(e)}")

class ContactMessageDetail(APIView):
    permission_classes = []  # No permission classes for public access
    
    def get(self, request, id):
        """Get a single contact message"""
        try:
            message = ContactMessage.objects.get(id=id)
            # Mark as read when viewed
            if not message.is_read:
                message.is_read = True
                message.status = 'read'
                message.save()
            
            serializer = ContactMessageSerializer(message)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        """Update a contact message (for status updates)"""
        try:
            message = ContactMessage.objects.get(id=id)
            serializer = ContactMessageSerializer(message, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Message updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except ContactMessage.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        """Delete a contact message"""
        try:
            message = ContactMessage.objects.get(id=id)
            message.delete()
            return Response({
                'success': True,
                'message': 'Message deleted successfully'
            }, status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)

class ContactMessageReplyView(APIView):
    permission_classes = []
    
    def post(self, request, id):
        """Reply to a contact message"""
        try:
            message = ContactMessage.objects.get(id=id)
            reply_message = request.data.get('reply', '')
            
            if not reply_message:
                return Response({
                    'success': False,
                    'error': 'Reply message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Send reply email to user
            subject = f"Re: {message.subject or 'Your inquiry'}"
            
            html_message = render_to_string('emails/contact_reply.html', {
                'name': message.name,
                'original_message': message.message,
                'reply': reply_message,
                'site_url': getattr(settings, 'SITE_URL', 'http://localhost:3000')
            })
            
            text_message = strip_tags(html_message)
            
            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[message.email],
            )
            email_msg.attach_alternative(html_message, "text/html")
            email_msg.send(fail_silently=False)
            
            # Update message status
            message.status = 'replied'
            message.save()
            
            return Response({
                'success': True,
                'message': 'Reply sent successfully',
                'data': ContactMessageSerializer(message).data
            }, status=status.HTTP_200_OK)
            
        except ContactMessage.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)