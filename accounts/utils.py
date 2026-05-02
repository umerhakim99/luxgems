from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from accounts.models import Profile


def user_is_admin_role(user: AbstractBaseUser | AnonymousUser) -> bool:
    """True if superuser or profile role is admin (ORM-only; safe if profile row is missing)."""
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    p = Profile.objects.filter(user=user).only("role").first()
    return p is not None and p.role == Profile.Role.ADMIN
