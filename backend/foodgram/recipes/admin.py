from django.contrib import admin

from .models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                     RecipeIngredients, ShoppingList, Tag)


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
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'pub_date',
        'in_favorites'
    )
    search_fields = ('name', 'author', 'pub_date', 'tags')
    list_filter = ('name', 'author', 'pub_date', 'tags')
    empty_value_display = '-empty-'
    
    def in_favorites(self, obj):
        '''The function counts total number
        of added recipes to favorites.
        '''
        return obj.favorites.count()


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
