from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]
    username = models.CharField(
        validators=(validate_username,),
        max_length=settings.STRING_LEN_FIELD_1,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Login пользователя'
    )
    email = models.EmailField(
        max_length=settings.STRING_LEN_FIELD_2,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email пользователя'
    )
    first_name = models.CharField(
        max_length=settings.STRING_LEN_FIELD_1,
        blank=True,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=settings.STRING_LEN_FIELD_1,
        blank=True,
        verbose_name='Фамилия пользоветля'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
