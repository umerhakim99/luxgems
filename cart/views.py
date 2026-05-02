from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.forms import DeliveryAddressForm
from catalog.models import Product

from .models import Cart, CartItem


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart = (
        Cart.objects.filter(pk=cart.pk)
        .prefetch_related("items__product__category")
        .first()
    )
    profile = request.user.profile
    if request.method == "POST" and request.POST.get("action") == "save_address":
        addr_form = DeliveryAddressForm(request.POST, instance=profile)
        if addr_form.is_valid():
            addr_form.save()
            messages.success(request, "Delivery address updated.")
            return redirect("cart:cart")
    else:
        addr_form = DeliveryAddressForm(instance=profile)
    return render(
        request,
        "cart/cart.html",
        {"cart": cart, "address_form": addr_form},
    )


@login_required
def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("catalog:showroom")
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    qty = max(1, int(request.POST.get("quantity", 1)))
    if qty > product.stock:
        messages.error(request, "Not enough stock available.")
        return redirect(product.get_absolute_url())
    cart = _get_or_create_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": qty})
    if not created:
        new_qty = item.quantity + qty
        if new_qty > product.stock:
            messages.error(request, "Cannot exceed available stock.")
            return redirect(product.get_absolute_url())
        item.quantity = new_qty
        item.save()
    messages.success(request, "Added to your collection bag. Continue to checkout when you are ready.")
    next_raw = (request.POST.get("next") or "").strip()
    default_next = reverse("orders:checkout")
    if next_raw.startswith("/") and not next_raw.startswith("//"):
        return redirect(next_raw)
    return redirect(default_next)


@login_required
def update_cart_item(request, item_id):
    if request.method != "POST":
        return redirect("cart:cart")
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = max(1, int(request.POST.get("quantity", 1)))
    if qty > item.product.stock:
        messages.error(request, "Quantity exceeds stock.")
    else:
        item.quantity = qty
        item.save()
    return redirect("cart:cart")


@login_required
def remove_cart_item(request, item_id):
    if request.method != "POST":
        return redirect("cart:cart")
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Item removed from bag.")
    return redirect("cart:cart")
