from django.core.management.base import BaseCommand
from faker import Faker
from apps.accounts.models import User

class Command(BaseCommand):
    help = 'Create fake users using the Fake package'

    def add_arguments(self, parser):
        # Add an argument for the number of users and user type
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of users to create (default: 20)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['admin', 'staff'],
            default='staff',
            help='Type of user to create: superuser or staff (default: staff)'
        )
    def handle(self, *args, **kwargs):
        fake = Faker()
        count = kwargs['count']
        user_type = kwargs['type']

        for _ in range(count):
            username = fake.user_name()
            email = fake.email()
            first_name = fake.first_name()
            last_name = fake.last_name()
            password = 'password123'

            if user_type == 'admin':
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'Admin {username} created successfully'))
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_staff=True
                )
                self.stdout.write(self.style.SUCCESS(f'Staff {username} created successfully'))

        self.stdout.write(self.style.SUCCESS(f'All {count} users created successfully'))



