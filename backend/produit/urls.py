from django.urls import path

from .views import (
    creer_categorie,
    creer_produit,
    detail_categorie,
    detail_produit,
    liste_categories,
    liste_produits,
    modifier_categorie,
    modifier_produit,
    supprimer_categorie,
    supprimer_produit,
)

app_name = 'produit'

urlpatterns = [
    path('', liste_produits, name='liste_produits'),
    path('ajouter/', creer_produit, name='creer_produit'),
    path('<int:produit_id>/', detail_produit, name='detail_produit'),
    path('<int:produit_id>/modifier/', modifier_produit, name='modifier_produit'),
    path('<int:produit_id>/supprimer/', supprimer_produit, name='supprimer_produit'),
    path('categories/', liste_categories, name='liste_categories'),
    path('categories/ajouter/', creer_categorie, name='creer_categorie'),
    path('categories/<int:categorie_id>/', detail_categorie, name='detail_categorie'),
    path('categories/<int:categorie_id>/modifier/', modifier_categorie, name='modifier_categorie'),
    path('categories/<int:categorie_id>/supprimer/', supprimer_categorie, name='supprimer_categorie'),
]