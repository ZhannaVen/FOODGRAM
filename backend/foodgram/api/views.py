from djoser.views import UserViewSet
from users.models import User
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CustomUserViewSet(UserViewSet):
    '''Getting data about users.
    '''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
