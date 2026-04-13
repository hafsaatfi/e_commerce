from django.urls import path
from .views import passer_commande

urlpatterns = [
    path('checkout/', passer_commande, name='checkout'),
]