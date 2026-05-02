from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from cart.models import Cart, CartItem
from catalog.models import Category, Product
from orders.models import Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    display_image_url = serializers.SerializerMethodField()
    price_pkr = serializers.SerializerMethodField()
    gallery_urls = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "short_description",
            "description",
            "price",
            "price_pkr",
            "category",
            "category_id",
            "material",
            "gemstone",
            "stock",
            "image_url",
            "image",
            "display_image_url",
            "gallery_urls",
            "rating_average",
            "rating_count",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "display_image_url",
            "price_pkr",
            "gallery_urls",
        )

    def get_price_pkr(self, obj):
        whole = int(Decimal(str(obj.price)).quantize(Decimal("1")))
        return f"Rs. {whole:,}"

    def get_display_image_url(self, obj):
        u = (obj.image_url or "").strip()
        if u:
            return u
        if not obj.image:
            return None
        request = self.context.get("request")
        path = obj.image.url
        if request and path.startswith("/"):
            return request.build_absolute_uri(path)
        return path

    def get_gallery_urls(self, obj):
        return obj.gallery_display_urls()


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
    )
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "items", "updated_at")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "unit_price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "total",
            "shipping_name",
            "shipping_email",
            "shipping_phone",
            "shipping_address",
            "notes",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("total", "created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role")

    def get_role(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.role if profile else None
