
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Player
from .forms import PlayerForm
from django.shortcuts import get_object_or_404
from .models import InjuryRecord
from .forms import InjuryForm
from .models import Event
from .forms import EventForm
from .models import AcademicRecord
from .forms import AcademicRecordForm
from .models import Equipment
from .forms import EquipmentForm
from collections import defaultdict
from .models import InventoryItem, BorrowRecord, Player
from .forms import InventoryItemForm, BorrowRecordForm



def player_list(request):
    players = Player.objects.all()
    grouped_players = defaultdict(list)

    for player in players:
        grouped_players[player.age_category].append(player)

    return render(request, 'player_list.html', {'grouped_players': grouped_players})



def home(request):
    return render(request, 'home.html')

def player_list(request):
    players = Player.objects.all()
    return render(request, 'player_list.html', {'players': players})

#__________________________________________________________________________


def add_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm()
    return render(request, 'add_player.html', {'form': form})

#__________________________________________________________________________

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

def delete_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        player.delete()
        return redirect('player_list')
    return render(request, 'delete_player.html', {'player': player})

#__________________________________________________________________________

def injury_list(request):
    injuries = InjuryRecord.objects.select_related('player').order_by('-date')
    return render(request, 'injury_list.html', {'injuries': injuries})

def add_injury(request):
    if request.method == 'POST':
        form = InjuryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm()
    return render(request, 'add_injury.html', {'form': form})


def edit_injury(request, injury_id):
    injury = get_object_or_404(InjuryRecord, pk=injury_id)
    if request.method == 'POST':
        form = InjuryForm(request.POST, instance=injury)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm(instance=injury)
    return render(request, 'edit_injury.html', {'form': form})

def player_injuries(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    injuries = InjuryRecord.objects.filter(player=player)
    return render(request, 'player_injuries.html', {'player': player, 'injuries': injuries})

#_________________________________________________________________________

def event_list(request):
    events = Event.objects.all().order_by('date', 'time')
    return render(request, 'event_list.html', {'events': events})

def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'add_event.html', {'form': form})

#__________________________________________________________________________

def academic_list(request):
    records = AcademicRecord.objects.select_related('player')
    return render(request, 'academic_list.html', {'records': records})

def add_academic_record(request):
    if request.method == 'POST':
        form = AcademicRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('academic_list')
    else:
        form = AcademicRecordForm()
    return render(request, 'add_academic_record.html', {'form': form})

def edit_academic_record(request, record_id):
    record = get_object_or_404(AcademicRecord, id=record_id)
    if request.method == 'POST':
        form = AcademicRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('academic_list')
    else:
        form = AcademicRecordForm(instance=record)
    return render(request, 'edit_academic_record.html', {'form': form})

def delete_academic_record(request, record_id):
    record = get_object_or_404(AcademicRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
        return redirect('academic_list')
    return render(request, 'delete_academic_record.html', {'record': record})


#__________________________________________________________________________

def inventory_list(request):
    items = InventoryItem.objects.all().order_by('name')
    return render(request, 'inventory_list.html', {'items': items})

# Add / Edit inventory — single view handles both
def inventory_form(request, item_id=None):
    item = None
    if item_id:
        item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save()
            # enforce available <= total
            if saved.available_quantity > saved.total_quantity:
                saved.available_quantity = saved.total_quantity
                saved.save()
            return redirect('inventory_list')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory_form.html', {'form': form, 'item': item})

def inventory_delete(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory_list')
    return render(request, 'delete_inventory.html', {'item': item})

# Borrow views
def borrow_form(request):
    # optional prefill ?item=ID
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
            # attempt to borrow from inventory
            if borrow.inventory_item.borrow(borrow.quantity):
                borrow.save()
                return redirect('borrow_list')
            else:
                form.add_error('quantity', 'Not enough available quantity')
    else:
        form = BorrowRecordForm(initial=initial)
    return render(request, 'borrow_form.html', {'form': form})

def borrow_list(request):
    borrows = BorrowRecord.objects.select_related('inventory_item', 'player').order_by('-created_at')
    return render(request, 'borrow_list.html', {'borrows': borrows})

def borrow_return(request, borrow_id):
    borrow = get_object_or_404(BorrowRecord, id=borrow_id)
    if request.method == 'POST':
        borrow.mark_returned()
        return redirect('borrow_list')
    return render(request, 'confirm_return.html', {'borrow': borrow})

# compatibility aliases for legacy urls
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
#__________________________________________________________________________

def player_list(request):
    players = Player.objects.all()
    grouped_players = defaultdict(list)

    for player in players:
        grouped_players[player.age_category].append(player)

    return render(request, 'player_list.html', {'grouped_players': grouped_players})

def home(request):
    return render(request, 'home.html')
