import random
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(user, otp_code):
    subject = 'Verify Your VUMA Tanzania Account'
    verification_url = f'http://localhost:3000/verify-otp?email={user.email}'
    
    html_message = render_to_string('email/verification_email.html', {
        'name': user.first_name or user.username,
        'otp_code': otp_code,
        'verification_url': verification_url,
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False