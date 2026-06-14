from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from easy_thumbnails.files import generate_all_aliases
from django.apps import apps

@shared_task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )

@shared_task
def generate_thumbnails(app_label, model_name, pk, field_name):
    """Асинхронно генерирует все миниатюры для поля файла."""
    try:
        model = apps.get_model(app_label, model_name)
        instance = model.objects.get(pk=pk)
        fieldfile = getattr(instance, field_name)
        if fieldfile:
            generate_all_aliases(fieldfile, include_global=True)
    except Exception as e:
        print(f"Error generating thumbnails: {e}")