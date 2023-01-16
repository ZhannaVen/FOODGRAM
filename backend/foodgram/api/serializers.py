from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow
from rest_framework.fields import SerializerMethodField


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
