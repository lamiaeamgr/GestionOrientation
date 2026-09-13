"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound
from django.urls import include, path
from django.views.generic import RedirectView


def _django_admin_desactive(request, extra=None):
    return HttpResponseNotFound()


urlpatterns = [
    path('admin/', _django_admin_desactive),
    path('admin/<path:extra>', _django_admin_desactive),
    path('comptes/', include('accounts.urls')),
    path('candidat/', include('candidats.urls')),
    path('formations/', include('formations.urls')),
    path('orientation/', include('orientation.urls')),
    path('evaluation/', include('evaluations.urls')),
    path('administration/', include('administration.urls')),
    path(
        'tableau-de-bord/admin/',
        RedirectView.as_view(pattern_name='administration:accueil', permanent=False),
    ),
    path('', include('conseil.urls')),
    path('', include('dashboard.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
