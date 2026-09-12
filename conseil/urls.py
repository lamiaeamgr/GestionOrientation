from django.urls import path

from . import views

app_name = 'conseil'

urlpatterns = [
    # Candidat
    path('conseillers/', views.liste_conseillers, name='conseillers'),
    path('reserver/<int:disponibilite_id>/', views.reserver, name='reserver'),
    path('mes-rendez-vous/', views.mes_rdv, name='mes_rdv'),
    path('annuler/<int:pk>/', views.annuler_rdv, name='annuler'),
    # Conseiller
    path('espace/', views.espace, name='espace'),
    path('disponibilites/', views.disponibilites, name='disponibilites'),
    path(
        'disponibilites/<int:pk>/supprimer/',
        views.supprimer_disponibilite,
        name='supprimer_dispo',
    ),
    path('rendez-vous/<int:pk>/', views.rdv_detail, name='rdv_detail'),
]
