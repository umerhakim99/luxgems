from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_role_required
from accounts.utils import user_is_admin_role
from cart.models import Cart
from catalog.models import Product

from .forms import CheckoutForm, OrderStatusForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = (
        Cart.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .first()
    )
    if not cart or not cart.items.exists():
        messages.warning(request, "Your collection bag is empty.")
        return redirect("cart:cart")
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Stock changed for {item.product.name}. Please update quantities.",
            )
            return redirect("cart:cart")
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = _place_order_from_cart(request.user, cart, form)
            except ValueError:
                messages.error(
                    request,
                    "Inventory changed while checking out. Please review your bag and try again.",
                )
                return redirect("cart:cart")
            messages.success(
                request,
                f"Order #{order.pk} confirmed. Payment: Cash on delivery (COD). "
                "Your jewellery will be packed and dispatched shortly — our team may contact you on the "
                "number you provided to confirm delivery.",
            )
            return redirect("orders:detail", pk=order.pk)
    else:
        prof = request.user.profile
        form = CheckoutForm(
            initial={
                "shipping_email": request.user.email,
                "shipping_name": (prof.full_name or request.user.get_full_name() or request.user.username).strip(),
                "shipping_phone": prof.phone,
                "province": prof.province,
                "city": prof.city,
                "street_address": prof.street_address,
                "postal_code": prof.postal_code,
            }
        )
    return render(
        request,
        "orders/checkout.html",
        {"form": form, "cart": cart},
    )


def _place_order_from_cart(user, cart, form):
    d = form.cleaned_data
    block = (
        f"{d['shipping_name']}\n{d['street_address']}\n"
        f"{d['city']}, {d['province']} {d['postal_code']}\nPakistan\n"
        f"Phone: {d['shipping_phone']}"
    )
    order = Order.objects.create(
        user=user,
        payment_method="cod",
        shipping_name=d["shipping_name"],
        shipping_email=d["shipping_email"],
        shipping_phone=d["shipping_phone"],
        shipping_province=d["province"],
        shipping_city=d["city"],
        shipping_postal_code=d["postal_code"],
        shipping_street=d["street_address"],
        shipping_address=block,
        notes=d.get("notes", ""),
        total=Decimal("0"),
    )
    total = Decimal("0")
    for line in cart.items.select_related("product"):
        p = line.product
        OrderItem.objects.create(
            order=order,
            product=p,
            quantity=line.quantity,
            unit_price=p.price,
        )
        total += p.price * line.quantity
        updated = Product.objects.filter(pk=p.pk, stock__gte=line.quantity).update(
            stock=F("stock") - line.quantity
        )
        if updated != 1:
            raise ValueError("Stock conflict")
    order.total = total
    order.save(update_fields=["total"])
    cart.items.all().delete()
    return order


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=pk)
    if order.user_id != request.user.id and not user_is_admin_role(request.user):
        messages.error(request, "You cannot view this order.")
        return redirect("catalog:home")
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_list(request):
    if user_is_admin_role(request.user):
        return redirect("accounts:admin_dashboard")
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


@admin_role_required
def admin_order_list(request):
    orders = Order.objects.select_related("user").order_by("-created_at")
    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)
    return render(
        request,
        "orders/admin_order_list.html",
        {"orders": orders, "statuses": Order.Status.choices},
    )


@admin_role_required
def admin_order_update_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated.")
            return redirect("orders:admin_order_list")
    else:
        form = OrderStatusForm(instance=order)
    return render(
        request,
        "orders/admin_order_status.html",
        {"form": form, "order": order},
    )
