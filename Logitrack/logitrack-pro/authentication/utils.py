from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_verified}"


email_verification_token = TokenGenerator()
password_reset_token = TokenGenerator()


def build_uid_token(user, generator):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = generator.make_token(user)
    return uidb64, token


def decode_uid(uidb64):
    return force_str(urlsafe_base64_decode(uidb64))


def send_verification_email(user, uidb64, token, request=None):
    link = f"http://localhost:5173/verify-email/{uidb64}/{token}/"
    send_mail(
        subject="Verify your LogiTrack Pro account",
        message=f"Hi {user.first_name or user.email}, verify your account: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


def send_password_reset_email(user, uidb64, token):
    link = f"http://localhost:5173/reset-password/{uidb64}/{token}/"
    send_mail(
        subject="Reset your LogiTrack Pro password",
        message=f"Hi {user.first_name or user.email}, reset your password: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
