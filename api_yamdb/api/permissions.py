from rest_framework import permissions


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == 'POST' and request.user.is_authenticated:
            return True
        elif request.method == 'PATCH':
            return request.user.is_staff or request.user == obj.author
        else:
            return False