from django.urls import path

from . import views

app_name = 'evaluations'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('<int:campagne_id>/', views.verifier, name='verifier'),
    path('<int:campagne_id>/repondre/', views.repondre, name='repondre'),
]
