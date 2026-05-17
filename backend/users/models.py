from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserActivity(models.Model):
    ACTION_VIEW_PRODUCT = 'view_product'
    ACTION_VIEW_CATEGORY = 'view_category'
    ACTION_ADD_TO_CART = 'add_to_cart'
    ACTION_PURCHASE = 'purchase'

    ACTION_CHOICES = (
        (ACTION_VIEW_PRODUCT, 'Vue produit'),
        (ACTION_VIEW_CATEGORY, 'Vue categorie'),
        (ACTION_ADD_TO_CART, 'Ajout au panier'),
        (ACTION_PURCHASE, 'Achat'),
    )

    utilisateur = models.ForeignKey('users.Utilisateur', on_delete=models.CASCADE)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    produit = models.ForeignKey('produit.Produit', on_delete=models.CASCADE, null=True, blank=True)
    categorie = models.ForeignKey('produit.Categorie', on_delete=models.CASCADE, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.utilisateur} - {self.action}"


class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')