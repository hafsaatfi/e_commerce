from django.urls import path
from .views import ajouter_au_panier, voir_panier, supprimer_article, modifier_quantite

urlpatterns = [
    path('', voir_panier, name='panier'),
    path('ajouter/<int:produit_id>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('supprimer/<int:article_id>/', supprimer_article),
    path('modifier/<int:article_id>/', modifier_quantite, name='modifier_quantite'),
]