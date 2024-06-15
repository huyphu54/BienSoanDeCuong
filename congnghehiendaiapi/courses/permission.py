from rest_framework import permissions


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

