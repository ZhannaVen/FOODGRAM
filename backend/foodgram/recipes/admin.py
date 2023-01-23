from django.contrib import admin

from .models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                     RecipeIngredients, ShoppingList, Tag, RecipeTags)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
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


class RecipeIngredientsAdmin(admin.StackedInline):
    model = RecipeIngredients
    autocomplete_fields = ('ingredient',)


class RecipeTagsAdmin(admin.StackedInline):
    model = RecipeTags
    autocomplete_fields = ('tag',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'pub_date',
        'in_favorites',
        'all_ingredients',
        'all_tags'
    )
    search_fields = ('name', 'author', 'pub_date')
    list_filter = ('name', 'author', 'pub_date', 'tags')
    inlines = (RecipeIngredientsAdmin, RecipeTagsAdmin)
    empty_value_display = '-empty-'
    
    def in_favorites(self, obj):
        """The function counts total number
        of added recipes to favorites.
        """
        return obj.favorites.count()

    def all_ingredients(self, obj):
        """The function displays all ingredients in the recipe.
        """
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])
    
    def all_tags(self, obj):
        """The function displays all tags in the recipe.
        """
        list_ = [_.name for _ in obj.tags.all()]
        return ', '.join(list_)


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
