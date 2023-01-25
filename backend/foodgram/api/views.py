from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.download import download_txt
from api.filters import IngredientFilter, RecipeFilter, TagFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CustomUserSerializer, FavoriteRecipesSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             ShoppingListSerializer, TagSerializer)
from recipes.models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                            RecipeIngredients, ShoppingList, Tag)
from users.models import User


class CustomUserViewSet(UserViewSet):
    '''Getting data about users.
    Adding users to subscriptions.
    Deleting users from subscriptions.
    Getting data about subscriptions.
    '''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Follow,
            user=user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    '''Getting data about tags.
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter
    permission_classes = (AllowAny,)


class IngredientViewSet(ReadOnlyModelViewSet):
    '''Getting data about ingredients.
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)


class RecipeViewSet(ModelViewSet):
    '''Getting data about recipes.
    Creating, editing, deleting recipes.
    Adding recipes to favorites and to shopping list.
    Downloading ingredients as file in txt.
    '''
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.add_to(
            request=request,
            pk=pk,
            serializers=FavoriteRecipesSerializer
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_from(request=request, pk=pk, model=FavoriteRecipes)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.add_to(
            request=request,
            pk=pk,
            serializers=ShoppingListSerializer
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_from(request=request, pk=pk, model=ShoppingList)

    @staticmethod
    def add_to(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        queryset = RecipeIngredients.objects.filter(
            recipe__shopping_list__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredient__name')
        return download_txt(queryset)
