from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow
from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status

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
    '''Serializer for displaying a list of tags or just one tag.
    '''
    class Meta:
        fields = (
            'name',
            'color',
            'slug',
        )
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    '''Serializer for displaying a list of ingredients or just one ingredient.
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
    id = IntegerField(write_only=True)
    amount = serializers.IntegerField()

    class Meta:
        fields = (
            'id',
            'amount'
        )
        model = RecipeIngredients


class RecipeWriteSerializer(serializers.ModelSerializer):
    '''Serializer for creating, editing, deleting a recipe.
    '''
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

    def validate_ingredints(self, data):
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
        
    def validate_tags(self, data):
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Add at least one tag')
        tags_list = []
        for item in tags:
            tag = get_object_or_404(Tag, id=item['id'])
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Tag should be unique!')
            tags_list.append(tag)

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
                detail='You have already subscribed this user',
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

