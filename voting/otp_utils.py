import secrets
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

OTP_EXPIRY_SECONDS = 30

def generate_otp():
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def send_otp_email(email, otp):
    send_mail(
        'Your login OTP for asictsvotes',
        f'Your one-time password is: {otp}\nThis OTP expires in 30 seconds.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

def store_otp(user_id, otp):
    cache.set(f'otp_{user_id}', otp, timeout=OTP_EXPIRY_SECONDS)

def verify_otp(user_id, otp):
    stored = cache.get(f'otp_{user_id}')
    return stored and stored == otp

def clear_otp(user_id):
    cache.delete(f'otp_{user_id}')