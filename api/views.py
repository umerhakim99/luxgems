from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from accounts.utils import user_is_admin_role
from cart.models import Cart, CartItem
from catalog.filters import ProductFilter
from catalog.models import Category, Product
from orders.models import Order

from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    CategorySerializer,
    OrderSerializer,
    ProductSerializer,
    UserSerializer,
)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("gallery_images")
        .filter(is_active=True)
    )
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ("name", "short_description", "gemstone", "description")
    ordering_fields = ("price", "created_at", "name")
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = Product.objects.select_related("category").prefetch_related("gallery_images").all()
        if self.request.user.is_authenticated and user_is_admin_role(self.request.user):
            return qs.order_by("-created_at")
        return qs.filter(is_active=True).order_by("-created_at")

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole]


class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def list(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path="add")
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        qty = serializer.validated_data.get("quantity", 1)
        if qty > product.stock:
            return Response({"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": qty}
        )
        if not created:
            new_q = item.quantity + qty
            if new_q > product.stock:
                return Response({"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
            item.quantity = new_q
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path=r"items/(?P<item_id>\d+)/update")
    def update_item(self, request, item_id=None):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        qty = int(request.data.get("quantity", 1))
        if qty > item.product.stock:
            return Response({"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = max(1, qty)
        item.save()
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=item.cart_id)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"], url_path=r"items/(?P<item_id>\d+)/remove")
    def remove_item(self, request, item_id=None):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        item.delete()
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.prefetch_related("items__product__category").get(pk=cart.pk)
        return Response(CartSerializer(cart).data)


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user_is_admin_role(user):
            return Order.objects.prefetch_related("items__product__category").order_by(
                "-created_at"
            )
        return Order.objects.filter(user=user).prefetch_related(
            "items__product__category"
        ).order_by("-created_at")

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[permissions.IsAuthenticated, IsAdminRole],
    )
    def status(self, request, pk=None):
        order = self.get_object()
        st = request.data.get("status")
        if st not in dict(Order.Status.choices):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = st
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.select_related("profile").all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
