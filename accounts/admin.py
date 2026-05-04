from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "full_name",
        "phone",
        "province",
        "city",
        "postal_code",
    )
    list_filter = ("role", "province")
    search_fields = ("user__username", "user__email", "full_name", "phone", "city", "postal_code")
