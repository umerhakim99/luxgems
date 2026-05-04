from django import forms
from django.forms import ValidationError

from accounts.pakistan_address import PROVINCE_CHOICES, validate_pakistan_address

from .models import Order


class CheckoutForm(forms.Form):
    shipping_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": "lx-input"}))
    shipping_email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "lx-input"}))
    shipping_phone = forms.CharField(
        max_length=32, required=True, widget=forms.TextInput(attrs={"class": "lx-input"})
    )
    province = forms.ChoiceField(choices=[("", "Select province")] + list(PROVINCE_CHOICES), required=True)
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "lx-input", "placeholder": "Enter your city"})
    )
    street_address = forms.CharField(
        label="Street address",
        widget=forms.Textarea(attrs={"rows": 3, "class": "lx-textarea"}),
        required=True,
    )
    postal_code = forms.CharField(max_length=5, min_length=5, widget=forms.TextInput(attrs={"class": "lx-input"}))
    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2, "class": "lx-textarea"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["province"].widget.attrs.setdefault("class", "lx-select")

    def clean(self):
        data = super().clean()
        if any(self.errors):
            return data
        errs = validate_pakistan_address(
            province=data.get("province", ""),
            city=data.get("city", ""),
            postal_code=data.get("postal_code", ""),
            street_address=data.get("street_address", ""),
        )
        if errs:
            raise ValidationError({k: [v] for k, v in errs.items()})
        return data


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status",)
        widgets = {"status": forms.Select(attrs={"class": "lx-select"})}