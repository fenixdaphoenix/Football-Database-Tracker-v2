from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from main.models import Player, Event, InjuryRecord, AcademicRecord, InventoryItem, BorrowRecord, Contact

class Command(BaseCommand):
    help = 'Create user groups: Heads (all permissions) and Players (view only)'

    def handle(self, *args, **options):
        # Create groups
        heads_group, _ = Group.objects.get_or_create(name='Heads')
        players_group, _ = Group.objects.get_or_create(name='Players')
        
        # Clear existing permissions
        heads_group.permissions.clear()
        players_group.permissions.clear()
        
        models = [Player, Event, InjuryRecord, AcademicRecord, InventoryItem, BorrowRecord, Contact]
        
        # Assign ALL permissions to Heads
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            heads_group.permissions.add(*permissions)
        
        # Assign VIEW permissions only to Players
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            view_permission = Permission.objects.filter(
                content_type=content_type,
                codename__startswith='view'
            )
            players_group.permissions.add(*view_permission)
        
        self.stdout.write(self.style.SUCCESS('✓ Heads group: All permissions'))
        self.stdout.write(self.style.SUCCESS('✓ Players group: View only'))
        self.stdout.write(self.style.SUCCESS('Groups created successfully'))
