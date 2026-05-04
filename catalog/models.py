from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, max_length=140)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class Material(models.TextChoices):
        GOLD_18K = "18k_gold", "18K Gold"
        WHITE_GOLD = "white_gold", "White Gold"
        PLATINUM = "platinum", "Platinum"
        SILVER = "silver", "Sterling Silver"
        MIXED = "mixed", "Mixed metals"

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    material = models.CharField(
        max_length=32,
        choices=Material.choices,
        default=Material.GOLD_18K,
    )
    gemstone = models.CharField(max_length=120, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/%Y/%m/", blank=True, null=True)
    image_url = models.URLField(
        max_length=600,
        blank=True,
        help_text="Optional HTTPS image (Unsplash/Pexels/etc.). Shown instead of uploaded file when set.",
    )
    is_active = models.BooleanField(default=True)
    rating_average = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("4.50"),
        validators=[MinValueValidator(Decimal("1")), MaxValueValidator(Decimal("5"))],
    )
    rating_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            self.slug = base
            n = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base}-{n}"
                n += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def display_image_url(self) -> str | None:
        """Prefer remote `image_url`, then uploaded `image`."""
        remote = (self.image_url or "").strip()
        if remote:
            return remote
        if self.image:
            return self.image.url
        return None

    def gallery_display_urls(self) -> list[str]:
        """Primary image first, then extra gallery shots (deduped, max 6)."""
        urls: list[str] = []
        main = self.display_image_url
        if main:
            urls.append(main)
        for gi in self.gallery_images.all():
            u = gi.display_url
            if u and u not in urls:
                urls.append(u)
        return urls[:6]

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    """Additional product photos (angles / lifestyle); main hero uses Product.image / image_url."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image_url = models.URLField(
        max_length=600,
        blank=True,
        help_text="HTTPS image URL (shown when no file upload).",
    )
    image = models.ImageField(upload_to="products/gallery/%Y/%m/", blank=True, null=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "pk")

    @property
    def display_url(self) -> str | None:
        remote = (self.image_url or "").strip()
        if remote:
            return remote
        if self.image:
            return self.image.url
        return None

    def __str__(self) -> str:
        return f"Image for {self.product_id}"


class ProductReview(models.Model):
    """One review per user per product (authenticated customers)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "product"),
                name="unique_review_per_user_product",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.product}: {self.rating}★"
