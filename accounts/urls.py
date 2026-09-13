from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.inscription, name='register'),
    path('connexion/', views.ConnexionView.as_view(), name='login'),
    path('connexion-admin/', views.ConnexionAdminView.as_view(), name='login_admin'),
    path(
        'connexion-conseiller/',
        views.ConnexionConseillerView.as_view(),
        name='login_conseiller',
    ),
    path('deconnexion/', views.DeconnexionView.as_view(), name='logout'),
    path('deconnexion-admin/', views.DeconnexionAdminView.as_view(), name='logout_admin'),
    path(
        'deconnexion-conseiller/',
        views.DeconnexionConseillerView.as_view(),
        name='logout_conseiller',
    ),
]
