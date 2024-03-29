from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Author has full rights.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )
