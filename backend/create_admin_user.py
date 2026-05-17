#!/usr/bin/env python
"""
Script de création d'un compte administrateur.
À lancer dans le même répertoire que manage.py après une migration.

Usage:
    python create_admin_user.py [--username USERNAME] [--email EMAIL] [--password PASSWORD]
"""
import os
import sys
import argparse
import secrets
import string
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from users.models import Utilisateur


def generate_password(length: int = 12) -> str:
    """Générer un mot de passe sécurisé."""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description='Créer un compte administrateur')
    parser.add_argument('--username', '-u', default='admin', help='Nom d\'utilisateur (défaut: admin)')
    parser.add_argument('--email', '-e', default='admin@admin.com', help='Email (défaut: admin@admin.com)')
    parser.add_argument('--password', '-p', help='Mot de passe. Si omis, un mot de passe aléatoire est généré')
    parser.add_argument('--length', '-l', type=int, default=12, help='Longueur du mot de passe généré (défaut: 12)')
    args = parser.parse_args()

    # Vérifier si l'utilisateur existe déjà
    if Utilisateur.objects.filter(username=args.username).exists():
        print(f"⚠️  L'utilisateur '{args.username}' existe déjà.")
        response = input("Voulez-vous le supprimer et le recréer? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Opération annulée.")
            return
        Utilisateur.objects.filter(username=args.username).delete()
        print(f"✓ Utilisateur '{args.username}' supprimé.")

    # Générer le mot de passe si nécessaire
    password = args.password if args.password else generate_password(args.length)

    # Créer l'utilisateur administrateur
    try:
        admin_user = Utilisateur.objects.create_superuser(
            username=args.username,
            email=args.email,
            password=password,
        )
        # Définir le rôle en tant qu'admin
        admin_user.role = 'admin'
        admin_user.save()

        print("\n" + "="*50)
        print("✓ Compte administrateur créé avec succès!")
        print("="*50)
        print(f"  Username: {admin_user.username}")
        print(f"  Email: {admin_user.email}")
        print(f"  Mot de passe: {password}")
        print(f"  Rôle: {admin_user.role}")
        print(f"  Superuser: {admin_user.is_superuser}")
        print(f"  Staff: {admin_user.is_staff}")
        print("\n✓ Connecte-toi avec:")
        print(f"  - Username: {args.username}")
        print(f"  - Mot de passe: {password}")
        print("="*50)

    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
