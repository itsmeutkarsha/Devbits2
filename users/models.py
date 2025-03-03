from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    streak=models.IntegerField(default=0)
    codeforces_handle = models.CharField(max_length=100, unique=True, blank=True, null=True)  # New field

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
