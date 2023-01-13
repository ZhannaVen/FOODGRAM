from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .validators import validate_username


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
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
    bio = models.TextField(
        blank=True,
        verbose_name='Biography of the user'
    )
    confirmation_code = models.CharField(
        max_length=250,
        null=True,
        blank=False,
        default='00000',
        verbose_name='Confirmation code for the password'
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()



