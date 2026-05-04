from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from luxgems.admin_site import LuxAdminSite, EmailAdminAuthForm

admin.site.__class__ = LuxAdminSite
admin.site.login_form = EmailAdminAuthForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("accounts/", include("accounts.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("", include("catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)