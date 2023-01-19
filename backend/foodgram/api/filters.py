from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class IngredientFilter(FilterSet):
    '''Filter for searching the ingredient
    by writting just some first letters.
    '''
    name = filters.CharFilter(
        field_name='name', lookup_expr='startswith'
    )
    
    class Meta:
        model = Ingredient
        fields = []


class RecipeFilter(FilterSet):
    '''Filter for searching the recipes
    by tags or being in the list of favorites recipes
    or being in the list of recipes in shopping list.
    '''
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        lookup_expr='startswith',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_list = filters.BooleanFilter(
        method='filter_is_in_shopping_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_list__user=user)
        return queryset
