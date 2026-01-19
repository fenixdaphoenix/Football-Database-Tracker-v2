from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from main import views as main_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', main_views.logout_confirm, name='logout'),

    path('', main_views.home, name='home'),
    path('add-admin/', main_views.add_admin, name='add_admin'),

    # players
    path('players/add/', views.add_player, name='add_player'),
    path('players/', views.player_list, name='player_list'),
    path('players/edit/<int:player_id>/', views.edit_player, name='edit_player'),
    path('players/delete/<int:player_id>/', views.delete_player, name='delete_player'),

    # injuries 
    path('players/<int:player_id>/injuries/', views.player_injuries, name='player_injuries'),
    path('players/<int:player_id>/injuries/add/', views.add_injury, name='add_player_injury'),
    path('injuries/', views.injury_list, name='injury_list'),
    path('injuries/add/', views.add_injury, name='add_injury'),
    path('injuries/<int:pk>/edit/', views.edit_injury, name='edit_injury'),
    path('injuries/<int:pk>/delete/', views.delete_injury, name='delete_injury'),

    # events
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    # academics
    path('academics/', views.academic_list, name='academic_list'),
    path('academics/add/', views.add_academic, name='add_academic'),
    path('academics/<int:record_id>/edit/', views.edit_academic, name='edit_academic'),
    path('academics/delete/<int:record_id>/', views.delete_academic, name='delete_academic'),

    # inventory / equipment
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/<int:item_id>/edit/', views.edit_inventory, name='edit_inventory'),
    path('inventory/<int:item_id>/delete/', views.delete_inventory, name='delete_inventory'),

    # borrowing
    path('borrowed/', views.borrow_list, name='borrow_list'),
    path('borrow/add/', views.borrow_form, name='add_borrow_record'),
    path('borrow/<int:borrow_id>/return/', views.return_borrow, name='return_borrow'),

    # storage
    path('storage/', views.storage_list, name='storage_list'),
    path('storage/add/', views.add_storage, name='add_storage'),
    path('storage/<int:storage_id>/edit/', views.edit_storage, name='edit_storage'),

    path('contact/', views.contact_info, name='contact_info'),
    path('contact/add/', views.add_contact, name='add_contact'),
    path('contact/<int:contact_id>/edit/', views.edit_contact, name='edit_contact'),
    path('contact/<int:contact_id>/delete/', views.delete_contact, name='delete_contact'),
]