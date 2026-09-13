from django.urls import path

from . import views

app_name = 'conseil'

urlpatterns = [
    path('conseil/conseillers/', views.liste_conseillers, name='conseillers'),
    path('conseil/reserver/<int:disponibilite_id>/', views.reserver, name='reserver'),
    path('conseil/mes-rendez-vous/', views.mes_rdv, name='mes_rdv'),
    path('conseil/annuler/<int:pk>/', views.annuler_rdv, name='annuler'),
    path('espace-conseiller/', views.espace, name='espace'),
    path('espace-conseiller/disponibilites/', views.disponibilites, name='disponibilites'),
    path(
        'espace-conseiller/disponibilites/<int:pk>/supprimer/',
        views.supprimer_disponibilite,
        name='supprimer_dispo',
    ),
    path('espace-conseiller/rendez-vous/<int:pk>/', views.rdv_detail, name='rdv_detail'),
    path('espace-conseiller/dossier/<int:pk>/', views.dossier_candidat, name='dossier'),
]
