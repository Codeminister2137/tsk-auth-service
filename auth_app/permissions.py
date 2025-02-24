from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
import logging


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own data.
    """

    def has_object_permission(self, request, view, obj):

        # Check if the object's user attribute matches the logged-in user, or user is admin
        return request.user.is_superuser or obj.id == request.user.id


class IsAuthenticatedAndHasSpecialRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'editor')