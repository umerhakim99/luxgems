from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r"v1/categories", views.CategoryViewSet, basename="category")
router.register(r"v1/products", views.ProductViewSet, basename="product")
router.register(r"v1/cart", views.CartViewSet, basename="cart")
router.register(r"v1/orders", views.OrderViewSet, basename="order")
router.register(r"v1/users", views.UserViewSet, basename="user")

urlpatterns = [
    path("v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("v1/me/", views.me, name="me"),
    path("", include(router.urls)),
]
