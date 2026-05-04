from rest_framework.permissions import BasePermission

from accounts.utils import user_is_admin_role


class IsAdminRole(BasePermission):
    """Allow only users with admin profile role or superuser."""

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return user_is_admin_role(u)
