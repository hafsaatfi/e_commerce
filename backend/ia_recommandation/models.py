from django.db import models

# Create your models here.
from django.db import models
from users.models import Utilisateur

class IA_Recommandation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    list_produit_ids = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)