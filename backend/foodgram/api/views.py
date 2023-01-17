from djoser.views import UserViewSet
from users.models import User
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import get_user_model


User = get_user_model()

FILENAME = 'shopping_list.pdf'


class CustomUserViewSet(UserViewSet):
    '''Getting data about users.
    '''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


