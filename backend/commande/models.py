from django.db import models
from users.models import Utilisateur
from produit.models import Produit

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmer', 'Confirmée'),
        ('rejeter', 'Rejetée'),
    ]

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=50, default="en_attente", choices=STATUT_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)

    # Champs checkout
    full_name = models.CharField(max_length=120, default='')
    phone = models.CharField(max_length=20, default='')
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, default='')
    ville = models.CharField(max_length=120, default='')
    quartier = models.CharField(max_length=120, blank=True, null=True)
    skin_type = models.CharField(max_length=32, blank=True, null=True)
    delivery_method = models.CharField(max_length=32, blank=True, null=True)
    skin_problem = models.CharField(max_length=160, blank=True, null=True)
    note = models.TextField(blank=True, null=True)


class ArticleCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.quantite * self.prix