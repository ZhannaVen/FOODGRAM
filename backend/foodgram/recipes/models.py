from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Name of the tag',
    )
    color = models.CharField(
        max_length=7,
        default="#ffffff",
        unique=True,
        verbose_name='HEX color of the tag',
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='Slug of the tag'
    )
    
    class Meta():
        ordering = ['-name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Ingredient (models.Model):
    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Name of the tag'
    )
    measurement_unit = models.CharField(
        max_length=256,
        verbose_name='Unit of measurement',
    )

    class Meta():
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name[:settings.STRING_LEN]  


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
        default=None
    )
    cooking_time = models.PositiveIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Cooking time of the dish in minutes'
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ingredients in the recipe',
    )
    tag = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags of the recipe',
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


class RecipeIngredients (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ingredient of the recipe'
    )
    quantity = models.PositiveIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Ingredient quantity'
    )
     
    class Meta:
        ordering = ['ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='all_keys_unique_together')]
        verbose_name = 'Quantity of each ingredient'


class FavoriteRecipes (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Favorite Recipes of the user'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='favorites',
        verbose_name='User'
    )
    
    def __str__(self):
        return f'Favorite recipes of {self.user}'

    class Meta():
        ordering = ['-id']
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'


class ShoppingList (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Ingredients to buy'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='shopping_list',
        verbose_name='User'
    )

    def __str__(self):
        return f'Ingredients to buy for {self.user}'

    class Meta():
        ordering = ['-id']
        verbose_name = 'Ingredient to buy'
        verbose_name_plural = 'Ingredients to buy'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Subscribe to the author')

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriptions')]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'





