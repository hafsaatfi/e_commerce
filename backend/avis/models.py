from django.db import models

# Create your models here.
from django.db import models
from users.models import Utilisateur
from produit.models import Produit

class Avis(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)