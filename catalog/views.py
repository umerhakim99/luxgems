from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import admin_role_required

from .forms import ProductForm, ProductImageFormSet, ReviewForm
from .models import Category, Product, ProductReview
from .web_images import HERO_EDITORIAL, HERO_MAIN


def home(request):
    featured = Product.objects.filter(is_active=True).select_related("category")[:6]
    return render(
        request,
        "catalog/home.html",
        {
            "featured": featured,
            "hero_main_url": HERO_MAIN,
            "hero_editorial_url": HERO_EDITORIAL,
        },
    )


def showroom(request):
    qs = Product.objects.filter(is_active=True).select_related("category")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(short_description__icontains=q)
            | Q(gemstone__icontains=q)
        )
    cat = request.GET.get("category")
    if cat:
        qs = qs.filter(category_id=cat)
    material = request.GET.get("material")
    if material:
        qs = qs.filter(material=material)
    min_p = request.GET.get("min_price")
    max_p = request.GET.get("max_price")
    if min_p:
        qs = qs.filter(price__gte=min_p)
    if max_p:
        qs = qs.filter(price__lte=max_p)
    sort = request.GET.get("sort", "newest")
    if sort == "price_low":
        qs = qs.order_by("price", "name")
    elif sort == "price_high":
        qs = qs.order_by("-price", "name")
    else:
        qs = qs.order_by("-created_at", "name")
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.all()
    return render(
        request,
        "catalog/showroom.html",
        {
            "page_obj": page,
            "categories": categories,
            "materials": Product.Material.choices,
            "current_sort": sort,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("gallery_images"),
        slug=slug,
        is_active=True,
    )
    related = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    reviews = product.reviews.select_related("user").order_by("-created_at")[:20]
    user_review = None
    review_form = None
    if request.user.is_authenticated:
        user_review = ProductReview.objects.filter(user=request.user, product=product).first()
        if request.method == "POST" and request.POST.get("action") == "submit_review":
            if user_review:
                messages.warning(request, "You have already rated this piece.")
            else:
                review_form = ReviewForm(request.POST)
                if review_form.is_valid():
                    r = review_form.save(commit=False)
                    r.user = request.user
                    r.product = product
                    r.save()
                    messages.success(request, "Thank you — your rating has been published.")
                    return redirect(product.get_absolute_url())
        if review_form is None and not user_review:
            review_form = ReviewForm()
    elif request.method == "POST" and request.POST.get("action") == "submit_review":
        messages.info(request, "Please sign in to leave a rating.")
        return redirect(f"{reverse('accounts:login')}?next={request.path}")
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "gallery_urls": product.gallery_display_urls(),
            "related": related,
            "reviews": reviews,
            "user_review": user_review,
            "review_form": review_form,
        },
    )


@admin_role_required
def admin_product_list(request):
    qs = Product.objects.select_related("category").order_by("-created_at")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "catalog/admin/product_list.html", {"page_obj": page})


@admin_role_required
def admin_product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save()
                    formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
                    if not formset.is_valid():
                        raise ValueError("gallery")
                    formset.save()
            except ValueError:
                messages.error(request, "Fix gallery image errors below, then save again.")
                return render(
                    request,
                    "catalog/admin/product_form.html",
                    {"form": form, "formset": formset, "title": "New product"},
                )
            messages.success(request, "Product created.")
            return redirect("catalog:admin_product_list")
        formset = ProductImageFormSet(request.POST, request.FILES)
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    return render(
        request,
        "catalog/admin/product_form.html",
        {"form": form, "formset": formset, "title": "New product"},
    )


@admin_role_required
def admin_product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Product updated.")
            return redirect("catalog:admin_product_list")
        if not formset.is_valid():
            messages.error(request, "Fix gallery image errors below, then save again.")
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    return render(
        request,
        "catalog/admin/product_form.html",
        {
            "form": form,
            "formset": formset,
            "title": f"Edit: {product.name}",
            "product": product,
        },
    )


@admin_role_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product removed.")
        return redirect("catalog:admin_product_list")
    return render(
        request,
        "catalog/admin/product_confirm_delete.html",
        {"product": product},
    )
