from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView, LoginView, LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("", HomeView.as_view(), name="home"),
    path("core/", include("core.urls")),
    path("api/", include("core.api_urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
