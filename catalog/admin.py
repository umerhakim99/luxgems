from django.contrib import admin

from .models import Category, Product, ProductImage, ProductReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("product__name", "user__username", "comment")
    raw_id_fields = ("user", "product")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("sort_order", "image_url", "image")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "rating_average",
        "rating_count",
        "stock",
        "image_url",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "material", "is_active")
    search_fields = ("name", "gemstone", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ProductImageInline,)
