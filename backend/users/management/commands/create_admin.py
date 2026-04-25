from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update an admin account"

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Admin username")
        parser.add_argument("--password", required=True, help="Admin password")
        parser.add_argument("--email", default="", help="Admin email")

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = options["username"]
        password = options["password"]
        email = options["email"]

        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )

        user.email = email or user.email
        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin '{username}' created successfully."))
        else:
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Admin privileges updated."))
