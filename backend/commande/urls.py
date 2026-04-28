from django.urls import path
from .views import confirmation, passer_commande

urlpatterns = [
    path('checkout/', passer_commande, name='checkout'),
    path('confirmation/', confirmation, name='confirmation'),
]
