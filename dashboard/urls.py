from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.accueil_public, name='accueil'),
    path('tableau-de-bord/', views.home, name='home'),
    path('tableau-de-bord/candidat/', views.candidat, name='candidat'),
]
