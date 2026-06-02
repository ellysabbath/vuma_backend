import random
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.save()
            
            # Send OTP via email
            subject = 'Verify Your VUMA Tanzania Account'
            verification_url = f'https://vumatanzaniaa.web.app/verify-otp?email={user.email}'
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0B3B2F, #1a5c48); color: white; padding: 30px; text-align: center; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; letter-spacing: 5px; background: #f0f5ee; padding: 20px; text-align: center; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Welcome to VUMA Tanzania!</h2>
                    </div>
                    <div style="padding: 20px;">
                        <p>Dear <strong>{user.first_name or user.username}</strong>,</p>
                        <p>Thank you for registering. Use this OTP to verify your account:</p>
                        <div class="otp-code">{otp}</div>
                        <p>This OTP expires in 10 minutes.</p>
                        <p>You can verify your account by entering this code on the verification page.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
            Welcome to VUMA Tanzania!
            
            Dear {user.first_name or user.username},
            
            Thank you for registering. Your OTP verification code is: {otp}
            
            This code expires in 10 minutes.
            
            If you didn't request this, please ignore this email.
            """
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                email_sent = False
                print(f"Email error: {e}")
            
            return Response({
                'success': True,
                'message': 'User created successfully. OTP sent to your email.',
                'email': user.email,
                'email_sent': email_sent
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email, otp_code=otp)
            user.is_verified = True
            user.otp_code = ''
            user.save()
            
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            
            # Send welcome email
            welcome_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0B3B2F, #1a5c48); color: white; padding: 30px; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Account Verified!</h2>
                    </div>
                    <div style="padding: 20px;">
                        <p>Dear <strong>{user.first_name or user.username}</strong>,</p>
                        <p>Your email has been successfully verified!</p>
                        <p>You can now log in to your VUMA Tanzania account using your email address.</p>
                        <p>Welcome to the community!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                'Welcome to VUMA Tanzania!',
                f'Dear {user.first_name or user.username},\n\nYour email has been verified successfully!\n\nWelcome to the community!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=welcome_html,
                fail_silently=True,
            )
            
            return Response({
                'success': True,
                'message': 'Email verified successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        except User.DoesNotExist:
            return Response({
                'success': False, 
                'error': 'Invalid OTP or email'
            }, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                return Response({
                    'success': False,
                    'error': 'Email already verified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.save()
            
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .otp-code {{ font-size: 32px; font-weight: bold; background: #f0f5ee; padding: 20px; text-align: center; }}
                </style>
            </head>
            <body>
                <div style="padding: 20px;">
                    <h2>New Verification Code</h2>
                    <p>Dear {user.first_name or user.username},</p>
                    <p>Your new verification code is:</p>
                    <div class="otp-code">{otp}</div>
                    <p>This code expires in 10 minutes.</p>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                'New Verification Code - VUMA Tanzania',
                f'Your new OTP is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'New OTP sent to your email',
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email'
            }, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            if not user.is_verified:
                return Response({
                    'success': False,
                    'error': 'Please verify your email first. Check your inbox for OTP.',
                    'requires_verification': True
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate new OTP for login
            login_otp = str(random.randint(100000, 999999))
            user.otp_code = login_otp
            user.save()
            
            # Send login OTP via email
            login_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .otp-code {{ font-size: 32px; font-weight: bold; background: #f0f5ee; padding: 20px; text-align: center; }}
                </style>
            </head>
            <body>
                <div style="padding: 20px;">
                    <h2>Login Verification Code</h2>
                    <p>Dear <strong>{user.first_name or user.username}</strong>,</p>
                    <p>Use this OTP to log in to your account:</p>
                    <div class="otp-code">{login_otp}</div>
                    <p>This code expires in 10 minutes.</p>
                </div>
            </body>
            </html>
            """
            
            send_mail(
                'Login Verification Code - VUMA Tanzania',
                f'Your login OTP is: {login_otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=login_html,
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'OTP sent to your email for login',
                'email': user.email,
                'requires_otp': True
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No account found with this email. Please sign up first.'
            }, status=status.HTTP_404_NOT_FOUND)

class VerifyLoginOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        try:
            user = User.objects.get(email=email, otp_code=otp)
            user.otp_code = ''
            user.save()
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user