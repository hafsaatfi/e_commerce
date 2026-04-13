from django.urls import path
from .views import liste_produits

urlpatterns = [
    path('', liste_produits),
]