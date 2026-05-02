from django.conf import settings
from django.db import models

from accounts.pakistan_address import PROVINCE_CHOICES


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CUSTOMER = "customer", "Customer"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    province = models.CharField(max_length=32, blank=True, choices=PROVINCE_CHOICES)
    city = models.CharField(max_length=80, blank=True)
    street_address = models.TextField(blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.user.is_superuser

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
