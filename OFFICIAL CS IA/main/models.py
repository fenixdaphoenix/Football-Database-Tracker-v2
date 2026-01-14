from django.db import models
import datetime
from datetime import date
#_________________________________________________________________py

class Player(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    birth_year = models.IntegerField()
    jersey_number = models.IntegerField(unique=True)
    position = models.CharField(max_length=50)
    current_school = models.CharField(max_length=100)
    initial_year = models.IntegerField()

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    @property
    def age_category(self):
        age = self.age
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

class Equipment(models.Model):
    EQUIPMENT_TYPES = (
        ('jersey', 'Jersey'),
        ('cleats', 'Cleats'),
        ('shin_guard', 'Shin Guard'),
        ('ball', 'Ball'),
        ('other', 'Other'),
    )


    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.item_name} for {self.player.name}"
    
#________________________________________________________________

class InjuryRecord(models.Model):

    INJURY_STATUS = (
        ('recovering', 'Recovering'),
        ('cleared', 'Cleared'),
        ('critical', 'Critical'),
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date = models.DateField()
    injury_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.player.name} - {self.injury_type}"

#________________________________________________________________

class Event(models.Model):
    EVENT_TYPES = (
        ('game', 'Game'),
        ('training', 'Training'),
        ('tournament', 'Tournament'),
    )
    
    type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()
    time = models.TimeField(default=datetime.time(12, 0))
    location = models.CharField(max_length=100, default='Unknown')
    description = models.TextField(blank=True, default ="")

    def __str__(self):
        return f"{self.get_type_display()} on {self.date} at {self.time.strftime('%I:%M %p')}"
    

#________________________________________________________________

class AcademicRecord(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    school_year = models.CharField(max_length=20)  # e.g., "2023-2024"
    school_name = models.CharField(max_length=100)
    academic_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.player.name} - {self.school_year}"
#________________________________________________________________


class InventoryItem(models.Model):
    ITEM_TYPES = (
        ('jersey', 'Jersey'),
        ('cleats', 'Cleats'),
        ('shin_guard', 'Shin Guard'),
        ('ball', 'Ball'),
        ('other', 'Other'),
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

# compatibility alias if other code imports Equipment
Equipment = InventoryItem

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
# ...existing code...