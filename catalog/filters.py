import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.NumberFilter(field_name="category_id")
    material = django_filters.CharFilter(field_name="material")

    class Meta:
        model = Product
        fields = ("category", "material", "min_price", "max_price")
