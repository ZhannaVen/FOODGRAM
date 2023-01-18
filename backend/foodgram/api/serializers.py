from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    FavoriteRecipes,
    ShoppingList,
    RecipeIngredients
)


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Serializer for creating a new user (User registration).
    '''
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        
        def create(self, validated_data):
            user = User.objects.create(
                email=validated_data['email'],
                username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user


class CustomUserSerializer(UserSerializer):
    '''Serializer for getting user profile.
    Get_is_subscribed - shows whether the current user
    is following the one being viewed.
    '''
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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list tags or a chosen one.
    '''
    class Meta:
        fields = (
            'name',
            'color',
            'slug',
        )
        read_only_fields = (
            'name',
            'color',
            'slug',
        )
        lookup_field = ('slug',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list ingredients or a chosen one.
    '''
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
    '''Serializer for displaying a list of ingredients and their amount.
    Only needed for RecipeReadSerializer.
    '''
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
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
    '''Serializer for displaying a list of recipes.
    '''
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_list = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_list',
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
            'is_in_shopping_list'

        )
        model = Recipe
    
    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_list(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_list.filter(recipe=obj).exists()


class IngredientWriteSerializer(serializers.ModelSerializer):
    '''Serializer for adding an ingredient and its amount to the recipe.
    Only needed for RecipeWriteSerializer.
    '''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'amount'
        )
        model = RecipeIngredients


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''Serializer for adding, editing, deleting a recipe.
    '''
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = CustomUserSerializer()
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
        read_only_fields = ('author',)
        model = Recipe

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Add at least one ingredient')
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ingredient should be unique!')
            ingredients_list.append(ingredient)
        
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Add at least one tag')
        for tag in tags:
            if not Tag.objects.filter(name=tag).exists():
                raise serializers.ValidationError(
                    f'Tag {tag} does not exist!')
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Cooking time should be >= 1')
        return cooking_time

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), 
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
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
    '''Serializer for displaying a brief recipe.
    Onle needed for FavoriteRecipesSerilizer, ShoppingListSerislizer
    and FollowSerializer.
    '''
    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list of favorite recipes.
    '''
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
                'status': 'You has already added this recipe to favorite ones!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BriefRecipeSerializer(
            instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list of recipes for shopping.
    '''
    class Meta:
        model = ShoppingList
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return BriefRecipeSerializer(
            instance.recipe, context=context).data


class FollowSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list of subscriptions of the user.
    '''
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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
        model = Follow

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return BriefRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

