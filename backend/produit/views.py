from django.shortcuts import render
from .models import Produit

def liste_produits(request):
    produits = Produit.objects.all()
    return render(request, 'produits.html', {'produits': produits})