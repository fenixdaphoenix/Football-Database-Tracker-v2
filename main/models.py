from django.db import models
import datetime
from datetime import date
#_________________________________________________________________py

class Player(models.Model):
    POSITION_CHOICES = [
        ('Striker', 'Striker'),
        ('Winger', 'Winger'),
        ('Midfielder', 'Midfielder'),
        ('Defender', 'Defender'),
        ('Goalkeeper', 'Goalkeeper'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-Binary', 'Non-Binary'),
        ('N/A', 'Prefer not to say'),

    ]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    jersey_number = models.PositiveIntegerField(unique=True)  # Only 0 and above
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    current_school = models.CharField(max_length=100)
    initial_year = models.IntegerField()

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def age_category(self):
        age = self.age
        if age is None:
            return "Unknown"
        if age < 10:
            return "U10"
        elif age < 13:
            return "U13"
        elif age < 16:
            return "U16"
        elif age < 19:
            return "U19"
        else:
            return "Senior"

    def __str__(self):
        return self.name
#________________________________________________________________

#________________________________________________________________

class InventoryItem(models.Model):
    class Meta:
        db_table = 'main_equipment'
    ITEM_TYPES = (
        ('gym_equipment', 'Gym Equipment'),
        ('football_equipment', 'Football Equipment'),
        ('football_accessories', 'Football Accessories'),
        ('others', 'Others'),
    )
    CONDITION_CHOICES = (
        ('good', 'Good'),
        ('worn', 'Worn'),
        ('unusable', 'Unusable'),
    )

    name = models.CharField(max_length=150)
    item_type = models.CharField(max_length=50, choices=ITEM_TYPES, default='other')
    total_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.available_quantity}/{self.total_quantity})"

    def borrow(self, qty=1):
        if qty <= 0:
            return False
        if self.available_quantity >= qty:
            self.available_quantity -= qty
            self.save()
            return True
        return False

    def return_back(self, qty=1):
        self.available_quantity = min(self.total_quantity, self.available_quantity + qty)
        self.save()
        return True

class BorrowRecord(models.Model):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='borrows')
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    issue_date = models.DateField(default=date.today)
    return_date = models.DateField(null=True, blank=True)
    returned = models.BooleanField(default=False)
    condition_when_issued = models.CharField(max_length=20, choices=InventoryItem.CONDITION_CHOICES, default='good')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_returned(self):
        if not self.returned:
            self.inventory_item.return_back(self.quantity)
            self.returned = True
            self.return_date = date.today()
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.inventory_item.name} x{self.quantity} to {self.player.name} ({'returned' if self.returned else 'out'})"
    
#________________________________________________________________

class InjuryRecord(models.Model):
    DURATION_CHOICES = [
        ('short', 'Short Term'),
        ('long', 'Long Term'),
    ]

    INJURY_CHOICES = [
        ('muscle', 'Muscle Injury'),
        ('bone', 'Bone Injury'),
        ('joint', 'Joint Injury'),
        ('concussion', 'Concussion'),
        ('other', 'Other'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date_of_injury = models.DateField(null=True, blank=True)
    duration_type = models.CharField(max_length=10, choices=DURATION_CHOICES, default='short')
    injury_type = models.CharField(max_length=20, choices=INJURY_CHOICES, default='other')
    injury_treatment = models.TextField()
    recovery_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.player.name} - {self.injury_type} on {self.date_of_injury}"

#________________________________________________________________

class Event(models.Model):
    EVENT_TYPES = (
        ('game', 'Game'),
        ('training', 'Training'),
        ('tournament', 'Tournament'),
    )
    REPEAT_CHOICES = [
        ('none', 'Does not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Every 2 Weeks'),
        ('monthly', 'Monthly'),
    ]

    title = models.CharField(max_length=200, blank=False, default='')

    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    time = models.TimeField(default=datetime.time(12, 0))
    location = models.CharField(max_length=100, default='Unknown')
    description = models.TextField(blank=True, default ="")

    def days_until(self):
        today = date.today()
        return (self.date - today).days

    def __str__(self):
        return f"{self.get_type_display()} on {self.date} at {self.time.strftime('%I:%M %p')}"
    

#________________________________________________________________

class AcademicRecord(models.Model):
    player = models.OneToOneField('Player', on_delete=models.CASCADE)  # one record per player
    grade_level = models.CharField(max_length=50)
    average_score = models.FloatField(default=0)
    passing = models.BooleanField(default=True)
    school = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.player.name} - {self.grade_level}"
    

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Player)
def create_academic_record_for_new_player(sender, instance, created, **kwargs):
    if created:
        AcademicRecord.objects.get_or_create(player=instance, defaults={
            'grade_level': '',
            'average_score': 0,
            'passing': True,
            'school': instance.current_school or ''
        })

#________________________________________________________________

class Contact(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} - {self.role}"
