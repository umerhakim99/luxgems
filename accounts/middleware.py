from .models import Profile


class EnsureProfileMiddleware:
    """Create a Profile for authenticated users missing one (e.g. legacy accounts)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        u = request.user
        if u.is_authenticated:
            Profile.objects.get_or_create(
                user=u,
                defaults={"role": Profile.Role.CUSTOMER},
            )
        return self.get_response(request)
