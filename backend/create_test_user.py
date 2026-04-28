#!/usr/bin/env python
"""
Script de création d'utilisateur test.
À lancer dans le même répertoire que manage.py après une migration.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import Utilisateur

# Supprimer l'utilisateur test s'il existe déjà
Utilisateur.objects.filter(username='testuser').delete()

# Créer l'utilisateur test
user = Utilisateur.objects.create_user(
    username='testuser',
    email='test@ecommerce.com',
    password='Test1234!',  # mot de passe simple pour test
)

print("✓ Utilisateur créé avec succès!")
print(f"  Username: {user.username}")
print(f"  Email: {user.email}")
print(f"  Mot de passe: Test1234!")
print("\nConnecte-toi avec l'un de ces identifiants:")
print("  1. Username: testuser / Mot de passe: Test1234!")
print("  2. Email: test@ecommerce.com / Mot de passe: Test1234!")
