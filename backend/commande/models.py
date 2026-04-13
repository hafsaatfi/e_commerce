from django.db import models
from users.models import Utilisateur
from produit.models import Produit

class Commande(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=50, default="en_attente")
    date_creation = models.DateTimeField(auto_now_add=True)


class ArticleCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)