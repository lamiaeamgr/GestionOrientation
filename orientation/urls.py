from django.urls import path

from . import views

app_name = 'orientation'

urlpatterns = [
    path('demarrer/', views.demarrer, name='demarrer'),
    path('tentative/<int:pk>/', views.passer, name='passer'),
    path('resultats/<int:pk>/', views.resultats, name='resultats'),
    path('historique/', views.historique, name='historique'),
]
