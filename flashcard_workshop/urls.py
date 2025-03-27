from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from flashcard_workshop.flashcards.urls import flash_card_sets_router, flash_cards_router

urlpatterns = [
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("admin/", admin.site.urls),
    path("api/", include(flash_card_sets_router.urls)),
    path("api/", include(flash_cards_router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("__debug__/", include("debug_toolbar.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]
