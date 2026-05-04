from django.contrib.admin import AdminSite
from django.contrib.auth.forms import AuthenticationForm
from django import forms


class EmailAdminAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email address'
        self.fields['username'].widget = forms.EmailInput(
            attrs={
                'autofocus': True,
                'class': 'vTextField',
                'placeholder': 'you@example.com'
            }
        )


class LuxAdminSite(AdminSite):
    login_form = EmailAdminAuthForm
    site_header = 'Lux Gems Admin'
    site_title = 'Lux Gems Admin'