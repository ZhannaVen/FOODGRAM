from django.contrib import admin

from .models import (
    FavoriteRecipes,
    Follow,
    Ingredient,
    Recipe,
    RecipeIngredients,
    ShoppingList,
    Tag
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'pub_date',
    )
    search_fields = ('name', 'author', 'pub_date',)
    list_filter = ('name', 'author', 'pub_date',)
    empty_value_display = '-empty-'


class RecipeIngredientsAdmin(admin.StackedInline):
    model = RecipeIngredients
    autocomplete_fields = ('ingredient',)


@admin.register(FavoriteRecipes)
class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-empty-'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-empty-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user', 'author',)
    list_filter = ('user',)
    empty_value_display = '-empty-'
