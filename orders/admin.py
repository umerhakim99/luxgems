from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_method", "total", "created_at")
    list_filter = ("status",)
    search_fields = ("shipping_name", "shipping_email", "user__username")
    inlines = [OrderItemInline]
    readonly_fields = ("user", "total", "created_at", "updated_at")
