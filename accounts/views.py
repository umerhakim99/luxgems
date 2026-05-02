from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from orders.models import Order

from .decorators import admin_role_required, customer_dashboard_required
from .forms import LuxAuthenticationForm, RegisterForm
from .utils import user_is_admin_role


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome to Lux Gems. Your account is ready.")
        return response


class LuxLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LuxAuthenticationForm


class LuxLogoutView(LogoutView):
    next_page = reverse_lazy("catalog:home")


@customer_dashboard_required
def user_dashboard(request):
    if user_is_admin_role(request.user):
        return redirect("accounts:admin_dashboard")
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:10]
    return render(
        request,
        "accounts/user_dashboard.html",
        {"orders": orders},
    )


@admin_role_required
def admin_dashboard(request):
    from django.db.models import Sum
    from catalog.models import Product

    stats = {
        "product_count": Product.objects.filter(is_active=True).count(),
        "order_count": Order.objects.count(),
        "revenue": Order.objects.filter(status=Order.Status.DELIVERED).aggregate(
            t=Sum("total")
        )["t"]
            or 0,
        "pending_orders": Order.objects.exclude(
            status__in=[Order.Status.DELIVERED, Order.Status.CANCELLED]
        ).count(),
    }
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:15]
    return render(
        request,
        "accounts/admin_dashboard.html",
        {"stats": stats, "recent_orders": recent_orders},
    )
