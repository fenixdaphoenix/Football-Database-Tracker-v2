from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Create HEADS and PLAYERS users with specific credentials'

    def handle(self, *args, **options):
        heads_group = Group.objects.get(name='Heads')
        players_group = Group.objects.get(name='Players')
        
        # Create HEADS user
        heads_user, created = User.objects.get_or_create(
            username='HEADS',
            defaults={'is_staff': True}
        )
        if created:
            heads_user.set_password('payatas123')
            heads_user.save()
            heads_group.user_set.add(heads_user)
            self.stdout.write(self.style.SUCCESS('✓ Created user: HEADS / payatas123'))
        else:
            # Update password if user exists
            heads_user.set_password('payatas123')
            heads_user.save()
            if not heads_user.groups.filter(name='Heads').exists():
                heads_group.user_set.add(heads_user)
            self.stdout.write(self.style.WARNING('Updated user: HEADS / payatas123'))
        
        # Create PLAYERS user
        players_user, created = User.objects.get_or_create(
            username='PLAYERS',
            defaults={'is_staff': False}
        )
        if created:
            players_user.set_password('gofootball123')
            players_user.save()
            players_group.user_set.add(players_user)
            self.stdout.write(self.style.SUCCESS('✓ Created user: PLAYERS / gofootball123'))
        else:
            # Update password if user exists
            players_user.set_password('gofootball123')
            players_user.save()
            if not players_user.groups.filter(name='Players').exists():
                players_group.user_set.add(players_user)
            self.stdout.write(self.style.WARNING('Updated user: PLAYERS / gofootball123'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ All users ready!'))
