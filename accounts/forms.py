from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.forms import ValidationError

from accounts.models import Profile
from accounts.pakistan_address import CITIES_BY_PROVINCE, PROVINCE_CHOICES, validate_pakistan_address


class LuxAuthenticationForm(AuthenticationForm):
    """Log in with the account email (legacy accounts may still use their original username)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email address"
        self.fields["username"].widget = forms.EmailInput(
            attrs={"class": "lx-input", "autocomplete": "email", "placeholder": "you@example.com"}
        )
        self.fields["password"].widget.attrs.setdefault("class", "lx-input")
        self.fields["password"].widget.attrs.setdefault("autocomplete", "current-password")

    def clean(self):
        from django.contrib.auth.models import User

        ident = (self.cleaned_data.get("username") or "").strip()
        if ident:
            user = User.objects.filter(email__iexact=ident).first()
            if user is None:
                user = User.objects.filter(username__iexact=ident).first()
            if user is not None:
                self.cleaned_data["username"] = user.username
        return super().clean()


class LuxPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.setdefault("class", "lx-input")


def _apply_address_validation(cleaned: dict) -> None:
    errs = validate_pakistan_address(
        province=cleaned.get("province", ""),
        city=cleaned.get("city", ""),
        postal_code=cleaned.get("postal_code", ""),
        street_address=cleaned.get("street_address", ""),
    )
    if errs:
        raise ValidationError({k: [v] for k, v in errs.items()})


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email (used to sign in)")
    full_name = forms.CharField(max_length=150, label="Full name", required=True)
    phone = forms.CharField(max_length=32, label="Mobile number", required=True)
    province = forms.ChoiceField(choices=[("", "Select province")] + list(PROVINCE_CHOICES), required=True)
    street_address = forms.CharField(
        label="Street address",
        widget=forms.Textarea(attrs={"rows": 3, "class": "lx-textarea"}),
        required=True,
    )
    postal_code = forms.CharField(max_length=5, min_length=5, label="Postal code", required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            del self.fields["username"]
        self.fields["city"] = forms.CharField(
            label="City",
            max_length=100,
            required=True,
            widget=forms.TextInput(attrs={"class": "lx-input", "placeholder": "Enter your city"}),
        )
        for name, field in self.fields.items():
            if name in ("password1", "password2", "street_address", "city", "province"):
                continue
            field.widget.attrs.setdefault("class", "lx-input")
        self.fields["province"].widget.attrs.setdefault("class", "lx-select")
        self.fields["password1"].widget.attrs.setdefault("class", "lx-input")
        self.fields["password2"].widget.attrs.setdefault("class", "lx-input")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        if User.objects.filter(username__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        data = super().clean()
        if any(self.errors):
            return data
        _apply_address_validation(data)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].strip().lower()
        user.username = email
        user.email = email
        fn = self.cleaned_data["full_name"].strip()
        parts = fn.split(None, 1)
        user.first_name = parts[0][:150]
        user.last_name = parts[1][:150] if len(parts) > 1 else ""
        if commit:
            user.save()
            profile = user.profile
            profile.full_name = fn
            profile.phone = self.cleaned_data["phone"].strip()
            profile.province = self.cleaned_data["province"]
            profile.city = self.cleaned_data["city"]
            profile.street_address = self.cleaned_data["street_address"].strip()
            profile.postal_code = self.cleaned_data["postal_code"].strip()
            profile.save()
        return user


class DeliveryAddressForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("full_name", "phone", "province", "city", "street_address", "postal_code")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "lx-input"}),
            "phone": forms.TextInput(attrs={"class": "lx-input"}),
            "province": forms.Select(attrs={"class": "lx-select"}),
            "city": forms.Select(attrs={"class": "lx-select"}),
            "street_address": forms.Textarea(attrs={"rows": 3, "class": "lx-textarea"}),
            "postal_code": forms.TextInput(attrs={"class": "lx-input", "maxlength": "5"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].widget = forms.TextInput(
            attrs={"class": "lx-input", "placeholder": "Enter your city"}
        )
        self.fields["province"].choices = [("", "Select province")] + list(PROVINCE_CHOICES)

    def clean(self):
        data = super().clean()
        if any(self.errors):
            return data
        _apply_address_validation(
            {
                "province": data.get("province", ""),
                "city": data.get("city", ""),
                "postal_code": data.get("postal_code", ""),
                "street_address": data.get("street_address", ""),
            }
        )
        return data
