from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("showroom/", views.showroom, name="showroom"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("dashboard/admin/products/", views.admin_product_list, name="admin_product_list"),
    path("dashboard/admin/products/new/", views.admin_product_create, name="admin_product_create"),
    path("dashboard/admin/products/<int:pk>/edit/", views.admin_product_edit, name="admin_product_edit"),
    path(
        "dashboard/admin/products/<int:pk>/delete/",
        views.admin_product_delete,
        name="admin_product_delete",
    ),
]
