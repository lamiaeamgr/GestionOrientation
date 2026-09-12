from django.urls import path

from . import views

app_name = 'candidats'

urlpatterns = [
    path('profil/', views.profil, name='profil'),
    path('interets/', views.interets, name='interets'),
    path('dossier/<int:pk>/', views.detail_profil, name='detail'),
]
