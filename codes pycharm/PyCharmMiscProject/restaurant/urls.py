from django.urls import path
from . import views

urlpatterns = [
    # Adresse vide '' -> On affiche la page d'accueil (Bienvenue)
    path('', views.home_view, name='home'),

    # Adresse 'menu/' -> On affiche la carte du jour (ton riz)
    path('menu/', views.menu_view, name='menu'),
]