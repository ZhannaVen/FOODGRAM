from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=settings.STRING_LEN_FIELD_3,
        blank=False,
        null=False,
        unique=True,
        verbose_name='Названи тега',
    )
    color = models.CharField(
        max_length=settings.STRING_LEN_FIELD_4,
        default="#ffffff",
        unique=True,
        verbose_name='HEX цвет тега',
    )
    slug = models.SlugField(
        max_length=settings.STRING_LEN_FIELD_3,
        unique=True,
        verbose_name='Slug тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:settings.STRING_LEN]


class Ingredient (models.Model):
    name = models.CharField(
        max_length=settings.STRING_LEN_FIELD_3,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=settings.STRING_LEN_FIELD_3,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_unit_unique_together')]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:settings.STRING_LEN]


class Recipe(models.Model):
    name = models.CharField(
        max_length=settings.STRING_LEN_FIELD_3,
        blank=False,
        null=False,
        unique=False,
        verbose_name='Название рецепта'
    )
    text = models.TextField(
        null=False,
        blank=False,
        verbose_name='Описание рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        'Image',
        upload_to='recipes/',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Время приготовления в минутах'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты в рецепте',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:settings.STRING_LEN]


class RecipeIngredients (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиенты в рецепте'
    )
    amount = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        ordering = ('ingredient',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='all_keys_unique_together')]
        verbose_name = 'Количество каждого ингредиента'


class RecipeTags (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes_tags',
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipes_tags',
        verbose_name='Теги рецепта'
    )

    class Meta:
        ordering = ('tag',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='recipe_tag_unique_together')]
        verbose_name = 'Теги рецепта'


class CommonModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Пользователь'
    )

    class Meta:
        abstract = True


class FavoriteRecipes (CommonModel):

    def __str__(self):
        return f'Любимые рецепты пользоваетля: {self.user}'

    class Meta:
        ordering = ('-id',)
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingList (CommonModel):

    def __str__(self):
        return f'Шопинг лист для: {self.user}'

    class Meta:
        ordering = ('-id',)
        default_related_name = 'shopping_list'
        verbose_name = 'Шопинг лист'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчики'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписки автора на других авторов')

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscriptions')]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
