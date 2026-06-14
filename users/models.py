from django.contrib.auth.models import AbstractUser
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
    )
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='buyer')
    company = models.CharField(max_length=40, blank=True)
    position = models.CharField(max_length=40, blank=True)
    avatar = ThumbnailerImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(f"DEBUG: save() called for user {self.pk}, avatar={self.avatar}")
        if self.avatar:
            from main.tasks import generate_thumbnails
            print("DEBUG: about to call generate_thumbnails.delay")
            generate_thumbnails.delay(
                app_label='users',
                model_name='User',
                pk=self.pk,
                field_name='avatar'
            )
            print("DEBUG: task dispatched")
        else:
            print("DEBUG: no avatar, task not sent")
    
    def __str__(self):
        return f"{self.email} ({self.type})"
