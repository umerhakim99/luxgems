from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Category, Product, ProductImage
from catalog.web_images import DEMO_PRODUCT_GALLERY_URLS, DEMO_PRODUCT_IMAGE_URLS


class Command(BaseCommand):
    help = "Create demo categories and products inspired by the Lux Gems showroom."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not set HTTPS image_url or clear uploaded files for demo products.",
        )

    def handle(self, *args, **options):
        skip_images = options["skip_images"]
        rings, _ = Category.objects.get_or_create(
            slug="rings",
            defaults={"name": "Rings"},
        )
        necklaces, _ = Category.objects.get_or_create(
            slug="necklaces",
            defaults={"name": "Necklaces"},
        )
        bracelets, _ = Category.objects.get_or_create(
            slug="bracelets",
            defaults={"name": "Bracelets"},
        )
        earrings, _ = Category.objects.get_or_create(
            slug="earrings",
            defaults={"name": "Earrings"},
        )

        demo = [
            {
                "name": "Diamond Necklace",
                "slug": "diamond-necklace",
                "short": "18K Gold with diamonds",
                "desc": "A timeless strand featuring brilliant-cut diamonds set in warm 18K gold.",
                "price": Decimal("485000"),
                "rating_average": Decimal("4.80"),
                "rating_count": 24,
                "category": necklaces,
                "material": Product.Material.GOLD_18K,
                "gemstone": "Diamond",
                "stock": 8,
            },
            {
                "name": "Sapphire Ring",
                "slug": "sapphire-ring",
                "short": "White Gold with sapphire",
                "desc": "Deep blue sapphire center stone with a refined white gold band.",
                "price": Decimal("375000"),
                "rating_average": Decimal("4.60"),
                "rating_count": 18,
                "category": rings,
                "material": Product.Material.WHITE_GOLD,
                "gemstone": "Sapphire",
                "stock": 12,
            },
            {
                "name": "Gemstone Bracelet",
                "slug": "gemstone-bracelet",
                "short": "Platinum with mixed gems",
                "desc": "Platinum links showcasing a curated mix of precious gemstones.",
                "price": Decimal("635000"),
                "rating_average": Decimal("4.90"),
                "rating_count": 31,
                "category": bracelets,
                "material": Product.Material.PLATINUM,
                "gemstone": "Mixed",
                "stock": 5,
            },
            {
                "name": "Diamond Earrings",
                "slug": "diamond-earrings",
                "short": "White Gold studs",
                "desc": "Classic studs with exceptional fire and clarity.",
                "price": Decimal("248000"),
                "rating_average": Decimal("4.90"),
                "rating_count": 42,
                "category": earrings,
                "material": Product.Material.WHITE_GOLD,
                "gemstone": "Diamond",
                "stock": 20,
            },
            {
                "name": "Statement Necklace",
                "slug": "statement-necklace",
                "short": "18K Gold with emeralds",
                "desc": "Bold silhouette with vivid emeralds for evening elegance.",
                "price": Decimal("572000"),
                "rating_average": Decimal("4.50"),
                "rating_count": 15,
                "category": necklaces,
                "material": Product.Material.GOLD_18K,
                "gemstone": "Emerald",
                "stock": 4,
            },
            {
                "name": "Emerald Ring",
                "slug": "emerald-ring",
                "short": "Platinum with emerald",
                "desc": "Platinum setting with a striking emerald centerpiece.",
                "price": Decimal("545000"),
                "rating_average": Decimal("4.85"),
                "rating_count": 28,
                "category": rings,
                "material": Product.Material.PLATINUM,
                "gemstone": "Emerald",
                "stock": 7,
            },
        ]

        created = 0
        for row in demo:
            defaults = {
                "name": row["name"],
                "short_description": row["short"],
                "description": row["desc"],
                "price": row["price"],
                "rating_average": row["rating_average"],
                "rating_count": row["rating_count"],
                "category": row["category"],
                "material": row["material"],
                "gemstone": row["gemstone"],
                "stock": row["stock"],
                "is_active": True,
            }

            obj, was_created = Product.objects.update_or_create(
                slug=row["slug"],
                defaults=defaults,
            )
            if was_created:
                created += 1

            if not skip_images:
                if obj.image:
                    obj.image.delete(save=False)
                obj.image = None
                obj.image_url = DEMO_PRODUCT_IMAGE_URLS[row["slug"]]
                obj.save(update_fields=["image", "image_url"])
                ProductImage.objects.filter(product=obj).delete()
                for i, url in enumerate(DEMO_PRODUCT_GALLERY_URLS.get(row["slug"], [])):
                    ProductImage.objects.create(
                        product=obj,
                        image_url=url,
                        sort_order=i,
                    )

        self.stdout.write(self.style.SUCCESS(f"Demo catalog ready. New products: {created}."))
        if skip_images:
            self.stdout.write("Images skipped (--skip-images).")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Demo products use HTTPS image_url (Unsplash/Pexels). "
                    "Uploaded files cleared for those slugs."
                )
            )
        self.stdout.write(
            "Promote an admin user (use the account email as username for email-registered users): "
            "`python manage.py shell -c \"from django.contrib.auth.models import User; "
            "from accounts.models import Profile; u=User.objects.get(email='you@example.com'); "
            "p, _ = Profile.objects.get_or_create(user=u); p.role=Profile.Role.ADMIN; p.save()\"`"
        )
