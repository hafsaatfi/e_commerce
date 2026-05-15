from django.urls import path
from .views import commande_index, confirmation, passer_commande

urlpatterns = [
    path('', commande_index, name='commande-index'),
    path('checkout/', passer_commande, name='checkout'),
    path('confirmation/', confirmation, name='confirmation'),
]
