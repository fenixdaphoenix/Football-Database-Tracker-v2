from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Create sample users and assign to groups'

    def add_arguments(self, parser):
        parser.add_argument('--create-heads', action='store_true', help='Create sample head users')
        parser.add_argument('--create-players', action='store_true', help='Create sample player users')

    def handle(self, *args, **options):
        heads_group = Group.objects.get(name='Heads')
        players_group = Group.objects.get(name='Players')
        
        if options['create_heads']:
            # Create head users
            head_users = [
                {'username': 'coach1', 'password': 'Coach@123', 'first_name': 'John', 'last_name': 'Coach'},
                {'username': 'coach2', 'password': 'Coach@456', 'first_name': 'Jane', 'last_name': 'Coach'},
            ]
            for user_data in head_users:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={'first_name': user_data['first_name'], 'last_name': user_data['last_name']}
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    heads_group.user_set.add(user)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created head user: {user_data["username"]} / {user_data["password"]}'))
                else:
                    self.stdout.write(f'User {user_data["username"]} already exists')
        
        if options['create_players']:
            # Create player users
            player_users = [
                {'username': 'player1', 'password': 'Player@123', 'first_name': 'Mike', 'last_name': 'Player'},
                {'username': 'player2', 'password': 'Player@456', 'first_name': 'Sarah', 'last_name': 'Player'},
            ]
            for user_data in player_users:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={'first_name': user_data['first_name'], 'last_name': user_data['last_name']}
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    players_group.user_set.add(user)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created player user: {user_data["username"]} / {user_data["password"]}'))
                else:
                    self.stdout.write(f'User {user_data["username"]} already exists')
