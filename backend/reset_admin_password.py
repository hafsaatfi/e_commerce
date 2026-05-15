from pathlib import Path
import os
import sys
import argparse
import secrets
import string


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from django.contrib.auth import get_user_model


def generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    parser = argparse.ArgumentParser(description='Reset password for users with email admin@admin.com')
    parser.add_argument('--password', '-p', help='Password to set. If omitted, a random password is generated and printed.')
    parser.add_argument('--length', '-l', type=int, default=12, help='Length for generated password (default: 12)')
    parser.add_argument('--list-all', action='store_true', help='List all users and their emails then exit')
    parser.add_argument('--id', type=int, help='Target user id to update')
    parser.add_argument('--username', help='Target username to update')
    args = parser.parse_args()

    if args.list_all:
        User = get_user_model()
        users = User.objects.all()
        if not users.exists():
            print('Aucun utilisateur dans la base.')
            return
        print('Liste des utilisateurs:')
        for u in users:
            print(f'id={u.id} username={getattr(u, "username", None)} email={getattr(u, "email", None)} is_superuser={u.is_superuser} is_staff={u.is_staff} is_active={u.is_active}')
        return

    # Determine target users
    User = get_user_model()
    if args.id:
        users = User.objects.filter(id=args.id)
    elif args.username:
        users = User.objects.filter(username__iexact=args.username)
    else:
        users = User.objects.filter(email__iexact='admin@admin.com')

    if args.password:
        new_password = args.password
    else:
        new_password = generate_password(args.length)

    if not users.exists():
        print('Aucun utilisateur trouvé.')
        return

    count = 0
    for u in users:
        u.set_password(new_password)
        u.save()
        count += 1

    print(f'Mot de passe mis à jour pour {count} utilisateur(s).')
    print('Nouveau mot de passe:', new_password)


if __name__ == '__main__':
    main()
