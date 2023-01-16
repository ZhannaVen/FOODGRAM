from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (USER, 'User')
    ]
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        unique=True,
        blank=False,
        null=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email of the user'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Name of the user'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Family name of the user'
    )
    role = models.CharField(
        max_length=25,
        choices=USER_ROLE_CHOICES,
        default=USER,
        blank=True,
        verbose_name='Role of the user'
    )
    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name'
    ]
    
    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
