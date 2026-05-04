from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_view, name="cart"),
    path("add/<int:product_id>/", views.add_to_cart, name="add"),
    path("line/<int:item_id>/update/", views.update_cart_item, name="update_line"),
    path("line/<int:item_id>/remove/", views.remove_cart_item, name="remove_line"),
]
