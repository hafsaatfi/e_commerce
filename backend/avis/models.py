from django.db import models

# Create your models here.
from django.db import models
from users.models import Utilisateur
from produit.models import Produit

class Avis(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    from django.core.validators import MinValueValidator, MaxValueValidator

    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'produit')
        ordering = ['-date_creation']

    def __str__(self):
        return f"Avis {self.note} - {self.produit} by {self.utilisateur}"