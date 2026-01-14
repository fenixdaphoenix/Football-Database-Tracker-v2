from django import forms
from .models import Player
from .models import InjuryRecord
from .models import Event
from .models import AcademicRecord
from .models import Equipment
from .models import InjuryRecord
from datetime import date
from .models import InventoryItem, BorrowRecord



class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'  # or list specific fields

#_______________________________________________________

class InjuryForm(forms.ModelForm):
    class Meta:
        model = InjuryRecord
        fields = '__all__'


#_______________________________________________________
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

#_______________________________________________________

class AcademicRecordForm(forms.ModelForm):
    class Meta:
        model = AcademicRecord
        fields = ['player', 'school_year', 'school_name', 'academic_notes']

#_______________________________________________________

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'item_type', 'total_quantity', 'available_quantity', 'condition', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class BorrowRecordForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['inventory_item', 'player', 'quantity', 'issue_date', 'condition_when_issued', 'notes']
        widgets = {
            'issue_date': forms.SelectDateWidget(years=range(2000, date.today().year + 2)),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }