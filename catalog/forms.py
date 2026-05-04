from django import forms
from django.forms import inlineformset_factory

from catalog.models import Product, ProductImage, ProductReview


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "comment")
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={"class": "lx-select"},
            ),
            "comment": forms.Textarea(
                attrs={"rows": 3, "class": "lx-textarea", "placeholder": "Optional short comment"}
            ),
        }


_input = {"class": "lx-input"}
_select = {"class": "lx-select"}
_area = {"class": "lx-textarea", "rows": 5}


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "category",
            "material",
            "gemstone",
            "stock",
            "image_url",
            "image",
            "rating_average",
            "rating_count",
            "is_active",
        )
        widgets = {
            "name": forms.TextInput(attrs=_input),
            "slug": forms.TextInput(attrs=_input),
            "short_description": forms.TextInput(attrs=_input),
            "description": forms.Textarea(attrs=_area),
            "price": forms.NumberInput(attrs=_input),
            "category": forms.Select(attrs=_select),
            "material": forms.Select(attrs=_select),
            "gemstone": forms.TextInput(attrs=_input),
            "stock": forms.NumberInput(attrs=_input),
            "image_url": forms.URLInput(attrs={**_input, "placeholder": "https://images.unsplash.com/..."}),
            "is_active": forms.CheckboxInput(attrs={"class": "lx-input"}),
            "image": forms.ClearableFileInput(attrs={"class": "lx-input"}),
            "rating_average": forms.NumberInput(attrs=_input),
            "rating_count": forms.NumberInput(attrs=_input),
        }


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("image_url", "image", "sort_order")
        widgets = {
            "image_url": forms.URLInput(attrs={**_input, "placeholder": "https://images.unsplash.com/..."}),
            "image": forms.ClearableFileInput(attrs={"class": "lx-input"}),
            "sort_order": forms.NumberInput(attrs=_input),
        }


ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=False,
    max_num=8,
)
