from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField

from recipes.models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                            RecipeIngredients, ShoppingList, Tag)
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Serializer for creating a new user
    (User registration) or getting user profile.
    Get_is_subscribed - shows whether the current user
    follows the one being viewed.
    """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of tags or just one tag.
    """
    class Meta:
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of ingredients or just one ingredient.
    """
    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',
        )
        lookup_field = ('name',)
        model = Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of ingredients and their amount.
    Only needed for RecipeReadSerializer.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )
        model = RecipeIngredients


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of recipes.
    """
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )
        model = Recipe

    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.shopping_list.filter(recipe=obj).exists()
        )


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Serializer for adding an ingredient and its amount to the recipe.
    Only needed for RecipeWriteSerializer.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'amount'
        )
        model = RecipeIngredients


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating, editing, deleting a recipe.
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        model = Recipe

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы 1 ингредиент!')
        ingredients_list = []
        for item in ingredients:
            ingredient = item['id']
            if ingredient in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиент должен быть уникальным!'
                })
            ingredients_list.append(ingredient)
            if int(item['amount']) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Необходимо добавить хотя бы 1 тег!'
            })
        tags_list = []
        for item in tags:
            if item in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тег должен быть уникальным!'
                })
            tags_list.append(item)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0!'
            })
        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data


class BriefRecipeSerializer(serializers.ModelSerializer):
    """Serializer for displaying a brief recipe.
    Onle needed for FavoriteRecipesSerilizer, ShoppingListSerislizer
    and FollowSerializer.
    """
    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of favorite recipes.
    """
    class Meta:
        fields = ('user', 'recipe')
        model = FavoriteRecipes

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if FavoriteRecipes.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise serializers.ValidationError({
                'status': 'Вы уже добавили этот рецепт в избранное!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BriefRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of recipes for shopping.
    """
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BriefRecipeSerializer(
            instance.recipe, context=context).data


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for displaying a list of subscriptions of the user.
    """
    is_subscribed = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        model = User
        read_only_fields = (
            'email',
            'username'
        )

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписались на этого автора!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='You can not subscribe youself',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return BriefRecipeSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
