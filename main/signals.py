from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, AcademicRecord

@receiver(post_save, sender=Player)
def create_academic_record(sender, instance, created, **kwargs):
    if created:
        AcademicRecord.objects.create(
            player=instance,
            school=instance.current_school  
        )
    else:
        if hasattr(instance, 'academicrecord'):
            instance.academicrecord.school = instance.current_school
            instance.academicrecord.save()
