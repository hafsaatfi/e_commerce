from django.urls import path
from .views import commande_index, confirmation, historique

urlpatterns = [
    path('', commande_index, name='commande-index'),
    path('confirmation/', confirmation, name='confirmation'),
    path('historique/', historique, name='historique'),
]
