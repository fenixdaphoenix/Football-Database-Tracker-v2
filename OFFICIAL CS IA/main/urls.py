from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.player_list, name='player_list'),
    path('players/add/', views.add_player, name='add_player'),
    path('players/edit/<int:player_id>/', views.edit_player, name='edit_player'),
    path('players/delete/<int:player_id>/', views.delete_player, name='delete_player'),
    path('players/<int:player_id>/injuries/', views.player_injuries, name='player_injuries'),
    path('players/<int:player_id>/injuries/add/', views.add_injury, name='add_injury'),
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('injuries/', views.injury_list, name='injury_list'),
    path('injuries/add/', views.add_injury, name='add_injury'),
    path('injuries/edit/<int:injury_id>/', views.edit_injury, name='edit_injury'),
    path('academics/', views.academic_list, name='academic_list'),
    path('academics/add/', views.add_academic_record, name='add_academic_record'),
    path('academics/edit/<int:record_id>/', views.edit_academic_record, name='edit_academic_record'),
    path('academics/delete/<int:record_id>/', views.delete_academic_record, name='delete_academic_record'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_form, name='add_inventory'),
    path('inventory/<int:item_id>/edit/', views.inventory_form, name='edit_inventory'),
    path('inventory/<int:item_id>/delete/', views.inventory_delete, name='delete_inventory'),
    path('borrow/', views.borrow_list, name='borrow_list'),
    path('borrow/add/', views.borrow_form, name='add_borrow_record'),
    path('borrow/<int:borrow_id>/return/', views.borrow_return, name='return_borrow'),

    # Legacy compatibility names (optional)
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.add_equipment, name='add_equipment'),
    path('equipment/edit/<int:equipment_id>/', views.edit_equipment, name='edit_equipment'),
    path('equipment/delete/<int:equipment_id>/', views.delete_equipment, name='delete_equipment'),




]


