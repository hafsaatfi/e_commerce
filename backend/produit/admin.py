from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Produit, Categorie

admin.site.register(Produit)
admin.site.register(Categorie)