from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    '''Admin has full rights.
    '''
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_staff
            )
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Author has full rights.
    '''
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.method in permissions.SAFE_METHODS
        )
