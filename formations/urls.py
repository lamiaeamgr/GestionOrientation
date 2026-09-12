from django.urls import path

from . import views

app_name = 'formations'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('<int:pk>/', views.detail, name='detail'),
    path('comparer/', views.comparer, name='comparer'),
]
