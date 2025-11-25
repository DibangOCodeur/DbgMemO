from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('Utilisateurs/', include('Utilisateurs.urls')), # Urls de l'application Utilisateur
    path('Dossier/',include('Dossier.urls')), # Urls de l'application Dossier
    path('', RedirectView.as_view(url='Utilisateurs/')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)