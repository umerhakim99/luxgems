from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("mine/", views.order_list, name="list"),
    path("<int:pk>/", views.order_detail, name="detail"),
    path("admin/orders/", views.admin_order_list, name="admin_order_list"),
    path("admin/orders/<int:pk>/status/", views.admin_order_update_status, name="admin_order_status"),
]
