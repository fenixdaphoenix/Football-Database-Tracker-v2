from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django import forms
import json
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import AdminUserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.shortcuts import redirect
from .models import  Player
from .forms import PlayerForm
from django.shortcuts import get_object_or_404
from .models import InjuryRecord
from .forms import InjuryForm
from .models import Event
from .forms import EventForm
from .models import AcademicRecord
from .forms import AcademicRecordForm
from collections import defaultdict
from datetime import date
from .models import InventoryItem, BorrowRecord
from .forms import InventoryItemForm, BorrowRecordForm
from .models import Contact
from .forms import ContactForm
from django.db.models import Sum
import re

@user_passes_test(lambda u: u.is_superuser)
def add_admin(request):
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True       
            user.save()
            messages.success(request, "Admin account created.")
            return redirect('home')
    else:
        form = AdminUserCreationForm()
    return render(request, 'add_admin.html', {'form': form})
#__________________________________________________________________________


def calculate_age(birth_date):
    if birth_date is None:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_age(birth_date):
    if birth_date is None:
        return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

#__________________________________________________________________________
#__________________________________________________________________________

@login_required
def home(request):
    # players distribution
    players = Player.objects.all()
    pos_counts = {}
    for p in players:
        pos = p.position or 'Unknown'
        pos_counts[pos] = pos_counts.get(pos, 0) + 1
    position_labels = list(pos_counts.keys())
    position_data = list(pos_counts.values())

    # ages (example buckets)
    age_buckets = {'<12':0,'12-14':0,'15-17':0,'18+':0}
    for p in players:
        try:
            age = p.age or 0
        except Exception:
            age = 0
        if age < 12: age_buckets['<12'] += 1
        elif age <= 14: age_buckets['12-14'] += 1
        elif age <= 17: age_buckets['15-17'] += 1
        else: age_buckets['18+'] += 1
    age_labels = list(age_buckets.keys())
    age_data = list(age_buckets.values())

    # genders
    gcounts = {}
    for p in players:
        g = (p.gender or 'Unknown')
        gcounts[g] = gcounts.get(g, 0) + 1
    gender_labels = list(gcounts.keys())
    gender_data = list(gcounts.values())

    # upcoming events next 7 days
    today = date.today()
    week = today + timedelta(days=7)
    upcoming_week_events = list(Event.objects.filter(date__gte=today, date__lte=week).order_by('date')[:10])

    # injuries summary (reuse logic from injury_list)
    injuries_qs = InjuryRecord.objects.select_related('player').all()
    long_count = 0
    short_count = 0
    type_counts = defaultdict(int)

    for inj in injuries_qs:
        dur = getattr(inj, 'duration_type', None) or getattr(inj, 'duration', None)
        classified = False
        if dur:
            s = str(dur).lower()
            if 'long' in s:
                long_count += 1
                classified = True
            elif 'short' in s:
                short_count += 1
                classified = True

        if not classified:
            start = getattr(inj, 'date_of_injury', None) or getattr(inj, 'injury_date', None)
            end = getattr(inj, 'recovery_date', None) or getattr(inj, 'expected_recovery', None)
            try:
                if start and end and hasattr(start, 'year') and hasattr(end, 'year'):
                    if (end - start).days > 21:
                        long_count += 1
                    else:
                        short_count += 1
                    classified = True
            except Exception:
                classified = False

        if not classified:
            short_count += 1

        if hasattr(inj, 'get_injury_type_display'):
            label = inj.get_injury_type_display() or (getattr(inj, 'injury_type', '') or 'Unknown')
        else:
            label = getattr(inj, 'injury_type', '') or 'Unknown'
        type_counts[label] += 1

    total_injuries = long_count + short_count
    injury_type_pairs = list(type_counts.items())
    injury_type_labels = [p[0] for p in injury_type_pairs]
    injury_type_data = [p[1] for p in injury_type_pairs]

    # schools passing % from AcademicRecord (example) — keep or remove if not used
    school_counts = {}
    school_pass_sum = {}
    for a in AcademicRecord.objects.select_related('player'):
        school = a.school or 'Unknown'
        school_counts.setdefault(school, 0)
        school_pass_sum.setdefault(school, 0)
        school_counts[school] += 1
        school_pass_sum[school] += (1 if (a.passing or False) else 0)
    school_labels = []
    school_pass_pct = []
    for s, cnt in school_counts.items():
        school_labels.append(s)
        pct = round((school_pass_sum[s] / cnt) * 100) if cnt else 0
        school_pass_pct.append(pct)

    context = {
        'position_labels': position_labels,
        'position_data': position_data,
        'age_labels': age_labels,
        'age_data': age_data,
        'gender_labels': gender_labels,
        'gender_data': gender_data,
        'upcoming_week_events': upcoming_week_events,
        # injuries context for the dashboard
        'long_injuries': long_count,
        'short_injuries': short_count,
        'total_injuries': total_injuries,
        'injury_type_pairs': injury_type_pairs,
        'injury_type_labels': injury_type_labels,
        'injury_type_data': injury_type_data,
        'school_labels': school_labels,
        'school_pass_pct': school_pass_pct,
    }
    return render(request, 'home.html', context)


@login_required
def player_list(request):
    players_qs = Player.objects.all()
    position_filter = request.GET.get("position")
    age_filter = request.GET.get("age_category")
    gender_filter = request.GET.get("gender")

    players = players_qs

    if position_filter:
        players = players.filter(position=position_filter)

    if gender_filter:
        players = players.filter(gender=gender_filter)

    if age_filter:
        players = [p for p in players if p.age_category == age_filter]

    positions = Player.POSITION_CHOICES
    genders = getattr(Player, 'GENDER_CHOICES', [('M','Male'),('F','Female'),('N/A', 'Prefer not to say')])
    age_categories = [
        ("U10", "Under 10"),
        ("U13", "Under 13"),
        ("U16", "Under 16"),
        ("U19", "Under 19"),
        ("Senior", "Senior"),
    ]

    return render(request, "player_list.html", {
        "players": players,
        "positions": positions,
        "age_categories": age_categories,
        "genders": genders,
        "position_filter": position_filter,
        "age_filter": age_filter,
        "gender_filter": gender_filter,
    })

#__________________________________________________________________________

@user_passes_test(lambda u: u.is_staff)
def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            AcademicRecord.objects.get_or_create(player=player, defaults={
                'grade_level': '',
                'average_score': 0,
                'passing': True,
                'school': player.current_school or ''
            })
            return redirect('player_list')
        else:
            print("PlayerForm errors:", form.errors)
    else:
        form = PlayerForm()
    return render(request, 'add_player.html', {'form': form})
#__________________________________________________________________________

@user_passes_test(lambda u: u.is_staff)
def edit_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'edit_player.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def delete_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        player.delete()
        return redirect('player_list')
    return render(request, 'delete_player.html', {'player': player})

#__________________________________________________________________________


#__________________________________________________________________________

@login_required
def injury_list(request):
    injury_filter = request.GET.get('injury_type', '').strip()
    injuries = InjuryRecord.objects.select_related('player').all()
    if injury_filter:
        injuries = injuries.filter(injury_type=injury_filter)

    long_count = 0
    short_count = 0
    type_counts = defaultdict(int)

    for inj in injuries:
        # classify by duration_type field if present
        dur = getattr(inj, 'duration_type', None) or getattr(inj, 'duration', None)
        classified = False
        if dur:
            s = str(dur).lower()
            if 'long' in s:
                long_count += 1
                classified = True
            elif 'short' in s:
                short_count += 1
                classified = True

        if not classified:
            # fallback: use date difference if available
            start = getattr(inj, 'date_of_injury', None) or getattr(inj, 'injury_date', None)
            end = getattr(inj, 'recovery_date', None) or getattr(inj, 'expected_recovery', None)
            try:
                if start and end and hasattr(start, 'year') and hasattr(end, 'year'):
                    if (end - start).days > 21:
                        long_count += 1
                    else:
                        short_count += 1
                    classified = True
            except Exception:
                classified = False

        if not classified:
            # default to short-term
            short_count += 1

        # injury type label for counts
        if hasattr(inj, 'get_injury_type_display'):
            label = inj.get_injury_type_display() or (getattr(inj, 'injury_type', '') or 'Unknown')
        else:
            label = getattr(inj, 'injury_type', '') or 'Unknown'
        type_counts[label] += 1

    total_injuries = long_count + short_count

    # prepare pairs and separate arrays for charts
    injury_type_pairs = list(type_counts.items())  # list of (label, count)
    injury_type_labels = [p[0] for p in injury_type_pairs]
    injury_type_data = [p[1] for p in injury_type_pairs]

    injury_types = getattr(InjuryRecord, 'INJURY_CHOICES', [])

    return render(request, 'injury_list.html', {
        'injuries': injuries,
        'injury_types': injury_types,
        'injury_filter': injury_filter,
        'long_injuries': long_count,
        'short_injuries': short_count,
        'total_injuries': total_injuries,
        'injury_type_pairs': injury_type_pairs,
        'injury_type_labels': injury_type_labels,
        'injury_type_data': injury_type_data,
    })

@user_passes_test(lambda u: u.is_staff)
def add_injury(request):
    if request.method == "POST":
        form = InjuryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm()
    return render(request, 'add_injury.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def edit_injury(request, pk):
    injury = get_object_or_404(InjuryRecord, pk=pk)
    if request.method == "POST":
        form = InjuryForm(request.POST, instance=injury)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm(instance=injury)
    return render(request, 'edit_injury.html', {'form': form, 'injury': injury})


@user_passes_test(lambda u: u.is_staff)
def delete_injury(request, pk):
    injury = get_object_or_404(InjuryRecord, pk=pk)
    if request.method == "POST":
        injury.delete()
        return redirect('injury_list')
    return render(request, 'injury_confirm_delete.html', {'injury': injury})

def player_injuries(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    injuries = InjuryRecord.objects.filter(player=player)
    return render(request, 'player_injuries.html', {'player': player, 'injuries': injuries})

#_________________________________________________________________________


#_________________________________________________________________________

@login_required
def event_list(request):
    type_filter = request.GET.get('type', '').strip()

    events = Event.objects.all().order_by('date', 'time')
    if type_filter:
        events = events.filter(type=type_filter)

    for event in events:
        event.days_until = event.days_until()

    event_types = Event.EVENT_TYPES
    return render(request, 'event_list.html', {
        'events': events,
        'event_types': event_types,
        'type_filter': type_filter,
    })
@user_passes_test(lambda u: u.is_staff)
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
        else:
            # show errors in console and let template display them
            print("Event form errors:", form.errors.as_json())
    else:
        form = EventForm()
    return render(request, 'add_event.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'add_event.html', {'form': form, 'event': event})

@user_passes_test(lambda u: u.is_staff)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'delete_event.html', {'event': event})

#__________________________________________________________________________

def _normalize_school_name(s):
    if not s:
        return ''
    s = s.strip().lower()
    # remove punctuation, keep letters/numbers and spaces, collapse whitespace
    s = re.sub(r'[^0-9a-z\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s


@login_required
def academic_list(request):
    qs = AcademicRecord.objects.select_related('player').order_by('player__name')

    school_filter = request.GET.get('school', '').strip()
    grade_filter = request.GET.get('grade', '').strip()

    raw_schools = [s for s in qs.values_list('player__current_school', flat=True) if s]
    school_map = {}
    for s in raw_schools:
        norm = _normalize_school_name(s)
        if norm and norm not in school_map:
            school_map[norm] = s.strip()

    if school_filter:
        chosen_label = school_map.get(school_filter)
        if chosen_label:
            qs = qs.filter(player__current_school__iexact=chosen_label)
        else:
            qs = qs.none()

    if grade_filter:
        qs = qs.filter(grade_level=grade_filter)

    schools = sorted([(k, v) for k, v in school_map.items()], key=lambda x: x[1].lower())

    grade_levels = sorted([g for g in AcademicRecord.objects.values_list('grade_level', flat=True).distinct() if g])

    return render(request, 'academic_list.html', {
        'records': qs,
        'schools': schools,
        'grade_levels': grade_levels,
    })
    
@user_passes_test(lambda u: u.is_staff)
def add_academic(request):
    if request.method == "POST":
        form = AcademicRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('academic_list')
    else:
        form = AcademicRecordForm()
    return render(request, 'add_academic.html', {'form': form})


@user_passes_test(lambda u: u.is_staff)
def edit_academic(request, record_id):
    record = get_object_or_404(AcademicRecord, id=record_id)
    if request.method == 'POST':
        form = AcademicRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('academic_list')
        else:
            print("Academic form errors:", form.errors)
    else:
        form = AcademicRecordForm(instance=record)
    return render(request, 'edit_academic.html', {'form': form, 'record': record})

@user_passes_test(lambda u: u.is_staff)
def delete_academic(request, pk):
    record = get_object_or_404(AcademicRecord, pk=pk)
    if request.method == "POST":
        record.delete()
        return redirect('academic_list')
    return render(request, 'delete_academic.html', {'record': record})

#__________________________________________________________________________
#__________________________________________________________________________

@login_required
def inventory_list(request):

    type_filter = request.GET.get('type', '').strip()

    items_qs = InventoryItem.objects.all().order_by('name')
    borrows_qs = BorrowRecord.objects.select_related('inventory_item', 'player')\
        .filter(returned=False).order_by('-created_at')

    if type_filter:
        items_qs = items_qs.filter(item_type=type_filter)
        borrows_qs = borrows_qs.filter(inventory_item__item_type=type_filter)

    item_types = InventoryItem.ITEM_TYPES  # tuple of (value,label)
    return render(request, 'inventory_list.html', {
        'items': items_qs,
        'borrows': borrows_qs,
        'item_types': item_types,
        'type_filter': type_filter,
    })

@user_passes_test(lambda u: u.is_staff)
def inventory_form(request, item_id=None):
    item = None
    if item_id:
        item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.available_quantity = saved.total_quantity
            saved.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory_form.html', {'form': form, 'item': item})

@user_passes_test(lambda u: u.is_staff)
def inventory_delete(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory_list')
    return render(request, 'delete_inventory.html', {'item': item})

@user_passes_test(lambda u: u.is_staff)
def borrow_form(request):
    initial = {}
    item_q = request.GET.get('item')
    if item_q:
        try:
            initial['inventory_item'] = InventoryItem.objects.get(id=int(item_q))
        except Exception:
            pass
    if request.method == 'POST':
        form = BorrowRecordForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            if borrow.inventory_item.borrow(borrow.quantity):
                borrow.save()
                return redirect('inventory_list')
            else:
                form.add_error('quantity', 'Not enough available quantity')
    else:
        form = BorrowRecordForm(initial=initial)
    return render(request, 'borrow_form.html', {'form': form})


@login_required
def borrow_list(request):
    type_filter = request.GET.get('type', '').strip()
    borrows = BorrowRecord.objects.select_related('inventory_item', 'player').order_by('-created_at')
    if type_filter:
        borrows = borrows.filter(inventory_item__item_type=type_filter)

    item_types = InventoryItem.ITEM_TYPES
    return render(request, 'borrow_list.html', {
        'borrows': borrows,
        'item_types': item_types,
        'type_filter': type_filter,
    })

@user_passes_test(lambda u: u.is_staff)
def borrow_return(request, borrow_id):
    borrow = get_object_or_404(BorrowRecord, id=borrow_id)
    if request.method == 'POST':
        borrow.mark_returned()
        return redirect('borrow_list')
    return render(request, 'confirm_return.html', {'borrow': borrow})

def equipment_list(request):
    return inventory_list(request)
def add_equipment(request):
    return inventory_form(request)
def edit_equipment(request, equipment_id):
    return inventory_form(request, item_id=equipment_id)
def delete_equipment(request, equipment_id):
    return inventory_delete(request, item_id=equipment_id)
def add_borrow(request):
    return borrow_form(request)
def storage_list(request):
    return inventory_list(request)

def add_storage(request):
    return inventory_form(request)

def edit_storage(request, storage_id):
    return inventory_form(request, item_id=storage_id)

def delete_storage(request, storage_id):
    return inventory_delete(request, item_id=storage_id)
def add_inventory(request):
    return inventory_form(request)

def edit_inventory(request, item_id):
    return inventory_form(request, item_id=item_id)

def delete_inventory(request, item_id):
    return inventory_delete(request, item_id=item_id)

def return_borrow(request, borrow_id):
    return borrow_return(request, borrow_id)

#__________________________________________________________________________




#__________________________________________________________________________

@login_required
def contact_info(request):
    contacts = Contact.objects.all()
    return render(request, "contact_info.html", {"contacts": contacts})

@user_passes_test(lambda u: u.is_staff)
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_info')
    else:
        form = ContactForm()
    return render(request, "add_contact.html", {"form": form})
