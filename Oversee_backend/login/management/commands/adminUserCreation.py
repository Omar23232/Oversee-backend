from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from login.models import UserRole

class Command(BaseCommand):
    help = 'Creates a new admin user with associated admin role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        try:
            # Check if user exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR(f'User {username} already exists'))
                return

            # Create the user
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            # Create associated admin role
            UserRole.objects.create(
                user=user,
                role='admin'
            )

            self.stdout.write(self.style.SUCCESS(f'Admin user {username} created successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}'))