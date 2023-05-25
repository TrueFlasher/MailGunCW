from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)


class Email(models.Model):
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email'
