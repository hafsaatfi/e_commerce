from django.db import models

class Categorie(models.Model):

    nom = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='produits/', null=True, blank=True)
    # Champ pour indiquer si le produit est un favori (Curated Favourite)
    is_favori = models.BooleanField(default=False, verbose_name="Produit favori (Curated Favourite)")

    def __str__(self):
        return self.nom