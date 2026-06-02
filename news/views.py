# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import News
# from .serializers import NewsSerializer

# class NewsList(APIView):
#     permission_classes = []
    
#     def get(self, request):
#         news = News.objects.all()
#         serializer = NewsSerializer(news, many=True)
#         return Response({
#             'success': True,
#             'data': serializer.data
#         }, status=status.HTTP_200_OK)
    
#     def post(self, request):
#         serializer = NewsSerializer(data=request.data)
#         if serializer.is_valid():
#             news = serializer.save()
#             return Response({
#                 'success': True,
#                 'message': 'News created successfully',
#                 'data': NewsSerializer(news).data
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             'success': False,
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# class NewsDetail(APIView):
#     permission_classes = []
    
#     def get(self, request, id):
#         try:
#             news = News.objects.get(id=id)
#             news.views += 1
#             news.save()
#             serializer = NewsSerializer(news)
#             return Response({
#                 'success': True,
#                 'data': serializer.data
#             }, status=status.HTTP_200_OK)
#         except News.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'News not found'
#             }, status=status.HTTP_404_NOT_FOUND)
    
#     def put(self, request, id):
#         try:
#             news = News.objects.get(id=id)
#             serializer = NewsSerializer(news, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response({
#                     'success': True,
#                     'message': 'News updated successfully',
#                     'data': serializer.data
#                 }, status=status.HTTP_200_OK)
#             return Response({
#                 'success': False,
#                 'errors': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
#         except News.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'News not found'
#             }, status=status.HTTP_404_NOT_FOUND)
    
#     def delete(self, request, id):
#         try:
#             news = News.objects.get(id=id)
#             news.delete()
#             return Response({
#                 'success': True,
#                 'message': 'News deleted successfully'
#             }, status=status.HTTP_200_OK)
#         except News.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'News not found'
#             }, status=status.HTTP_404_NOT_FOUND)

# class NewsLikeView(APIView):
#     permission_classes = []
    
#     def post(self, request, id):
#         try:
#             news = News.objects.get(id=id)
#             news.likes += 1
#             news.save()
#             return Response({
#                 'success': True,
#                 'message': 'News liked successfully',
#                 'likes': news.likes
#             }, status=status.HTTP_200_OK)
#         except News.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'error': 'News not found'
#             }, status=status.HTTP_404_NOT_FOUND)













from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from .models import News
from .serializers import NewsSerializer

User = get_user_model()

class NewsList(APIView):
    permission_classes = []
    
    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            news = serializer.save()
            
            # Send email notification to all users
            self.send_notification_emails(news)
            
            return Response({
                'success': True,
                'message': 'News created successfully and notifications sent',
                'data': NewsSerializer(news).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_notification_emails(self, news):
        """Send email notifications to all users about new news"""
        try:
            # Get all users
            all_users = User.objects.all()
            
            if not all_users.exists():
                print("No users found to send notifications")
                return
            
            # Email subject
            subject = f"New Update: {news.title}"
            
            # Prepare email content
            context = {
                'title': news.title,
                'content': news.content[:200] if news.content else '',
                'image_url': news.image_base64[:100] + '...' if news.image_base64 else None,
                'date': news.created_at.strftime('%B %d, %Y'),
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://vumatanzaniaa.web.app',
                'news_id': news.id
            }
            
            # Render HTML email template
            html_message = render_to_string('emails/news_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Alternative plain text message
            text_message = f"""
            New Update: {news.title}
            
            {news.content[:500]}...
            
            Read more: {context['site_url']}/news/{news.id}
            
            ---
            This is an automated notification from VUMA Tanzania.
            """
            
            # Get all user emails
            recipient_emails = list(all_users.values_list('email', flat=True))
            
            # Send emails in batches to avoid overwhelming the server
            batch_size = 50
            for i in range(0, len(recipient_emails), batch_size):
                batch = recipient_emails[i:i+batch_size]
                try:
                    # Use EmailMultiAlternatives for HTML email
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=text_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=batch,
                        bcc=batch,  # Use BCC to hide recipients from each other
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send(fail_silently=False)
                    
                    print(f"Sent notifications to {len(batch)} users")
                except Exception as e:
                    print(f"Error sending batch {i}: {str(e)}")
                    # Continue with next batch even if one fails
                    continue
                    
            print(f"Successfully sent news notifications to {len(recipient_emails)} users")
            
        except Exception as e:
            print(f"Error sending notification emails: {str(e)}")
            # Don't raise the exception - email failure shouldn't break the news creation

class NewsDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.views += 1
            news.save()
            serializer = NewsSerializer(news)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            news = News.objects.get(id=id)
            serializer = NewsSerializer(news, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'News updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.delete()
            return Response({
                'success': True,
                'message': 'News deleted successfully'
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)

class NewsLikeView(APIView):
    permission_classes = []
    
    def post(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.likes += 1
            news.save()
            return Response({
                'success': True,
                'message': 'News liked successfully',
                'likes': news.likes
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)