from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import InventoryItem, BorrowRecord
from django import forms
from django.contrib.auth.models import User
from .models import InventoryItem, Player
from .models import InjuryRecord
from .models import Event
from .models import AcademicRecord
from datetime import date
from .models import Contact

class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email",)

#_______________________________________________________

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'birth_date', 'jersey_number', 'gender', 'position', 'current_school', 'initial_year']
        widgets = {
            'birth_date': forms.SelectDateWidget(years=range(2005, date.today().year + 1)),  # Adjust years as needed
            'initial_year': forms.Select(choices=[(y, y) for y in range(2009, date.today().year + 1)]),
        }
#_______________________________________________________

class InjuryForm(forms.ModelForm):
    class Meta:
        model = InjuryRecord
        fields = ['player', 'date_of_injury', 'duration_type', 'injury_type', 'injury_treatment']
        widgets = {
            'date_of_injury': forms.SelectDateWidget(
                years=range(2024, date.today().year + 1),
                empty_label=("Year", "Month", "Day")
            ),
            'recovery_date': forms.SelectDateWidget(
                years=range(2024, date.today().year + 10),
                empty_label=("Year", "Month", "Day")
            ),
            'injury_treatment': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
        labels = {
            'injury_treatment': 'Injury Treatment',
            'duration_type': 'Injury Duration',
            'injury_type': 'Type of Injury',
        }


#_______________________________________________________

class EventForm(forms.ModelForm):
    time = forms.TimeField(
        required=True,
        input_formats=['%H:%M'],  
        widget=forms.TimeInput(format='%H:%M', attrs={
            'class': 'form-control',
            'placeholder': '24-hour, e.g. 14:30',
            'aria-label': 'Event time (HH:MM)'
        }),
        help_text='Enter time in 24-hour format (HH:MM), e.g. 14:30.'
    )

    class Meta:
        model = Event
        fields = ['title', 'type', 'date', 'time', 'location', 'description']  
        widgets = {
            'date': forms.SelectDateWidget(years=range(2024, 2031)),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_time(self):
        t = self.cleaned_data.get('time')
        if not t:
            raise forms.ValidationError("Enter a valid time in HH:MM (24-hour) format.")
        return t
#_______________________________________________________

class AcademicRecordForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('', 'Select grade'), ('K', 'K'), ('1', '1'), ('2', '2'), ('3', '3'),
        ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
        ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('Other', 'Other'),
    ]

    grade_level = forms.ChoiceField(choices=GRADE_CHOICES, required=False)

    average_score = forms.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'step': 'any', 'min': 0, 'max': 100})
    )

    class Meta:
        model = AcademicRecord
        fields = ['grade_level', 'average_score', 'school']
        widgets = {
            'school': forms.TextInput(),
        }

    def clean_average_score(self):
        val = self.cleaned_data.get('average_score')
        if val in (None, ''):
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            raise forms.ValidationError("Enter a number between 0 and 100.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        average_score = self.cleaned_data.get('average_score')
        instance.passing = average_score > 75 if average_score is not None else False
        if commit:
            instance.save()
        return instance
#_______________________________________________________

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
        
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'role', 'phone', 'email']

