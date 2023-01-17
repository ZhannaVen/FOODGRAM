from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow
from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

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
    '''Serializer for adding, changing, deleting a recipe.
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
    





