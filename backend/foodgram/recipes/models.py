from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.html import format_html


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Name of the tag'
    )
    hexcolor = models.CharField(
        max_length=7,
        default="#ffffff"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True
    )

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.hexcolor,
        )
    


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        unique=False,
        verbose_name='Name of the recipe'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Description of the recipe'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author of the recipe'
    )
    image = models.ImageField(
        'Image',
        upload_to='recipes/',
        blank=True,
        verbose_name='Image of the recipe'
    )
    cooking_time = models.PositiveIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Cooking time of the dish'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date of creation'
    )
    
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name[:settings.STRING_LEN]





