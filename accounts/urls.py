from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.inscription, name='register'),
    path('connexion/', views.ConnexionView.as_view(), name='login'),
    path('deconnexion/', LogoutView.as_view(), name='logout'),
]
