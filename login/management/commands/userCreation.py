from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from login.models import UserRole

class Command(BaseCommand):
    help = 'Creates a new regular user with normal user role'

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

            # Create regular user instead of superuser
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # Create associated user role
            UserRole.objects.create(
                user=user,
                role='user'  # Set role as normal user
            )

            self.stdout.write(self.style.SUCCESS(f'Regular user {username} created successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {str(e)}'))