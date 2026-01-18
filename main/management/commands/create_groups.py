from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create user groups: Heads and Players'

    def handle(self, *args, **options):
        # Create groups
        heads_group, created = Group.objects.get_or_create(name='Heads')
        players_group, created = Group.objects.get_or_create(name='Players')
        
        self.stdout.write(self.style.SUCCESS('Groups created successfully'))
