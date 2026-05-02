from decimal import Decimal

from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from catalog.models import Product, ProductReview


def _refresh_product_rating(product_id: int) -> None:
    agg = ProductReview.objects.filter(product_id=product_id).aggregate(
        avg=Avg("rating"),
        cnt=Count("id"),
    )
    cnt = agg["cnt"] or 0
    avg = agg["avg"]
    if cnt == 0:
        Product.objects.filter(pk=product_id).update(
            rating_average=Decimal("4.50"),
            rating_count=0,
        )
    else:
        Product.objects.filter(pk=product_id).update(
            rating_average=avg,
            rating_count=cnt,
        )


@receiver(post_save, sender=ProductReview)
def review_saved(sender, instance, **kwargs):
    _refresh_product_rating(instance.product_id)


@receiver(post_delete, sender=ProductReview)
def review_deleted(sender, instance, **kwargs):
    _refresh_product_rating(instance.product_id)
