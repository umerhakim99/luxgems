from django import template

from accounts.utils import user_is_admin_role

register = template.Library()


@register.simple_tag
def user_is_admin(user):
    """Use in templates instead of ``user.profile.is_admin_role`` (avoids descriptor errors)."""
    return user_is_admin_role(user)
