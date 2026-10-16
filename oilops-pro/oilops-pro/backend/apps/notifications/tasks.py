from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_email_notification(self, recipients, subject, body):
    if not recipients:
        return 0
    try:
        return send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
    except Exception as exc:  # pragma: no cover - network failures
        raise self.retry(exc=exc)
