from django.core.management.base import BaseCommand
from users.models import Utilisateur


class Command(BaseCommand):
    help = 'Create a default test user'

    def handle(self, *args, **options):
        # Supprimer l'ancien utilisateur s'il existe
        Utilisateur.objects.filter(username='admin').delete()

        # Créer l'utilisateur admin
        user = Utilisateur.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='admin123',
        )

        self.stdout.write(
            self.style.SUCCESS('✓ Utilisateur créé avec succès!')
        )
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Mot de passe: admin123')
        self.stdout.write(
            self.style.WARNING(
                '\nConnecte-toi à /users/login/ avec:\n'
                '  Username: admin\n'
                '  Mot de passe: admin123\n'
                '  OU Email: admin@admin.com + admin123'
            )
        )
