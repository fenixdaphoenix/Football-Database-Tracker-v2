from django.contrib import admin
from django.urls import path, include
from main import views as main_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Login / Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True  # prevents redirect loops
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ✅ Main homepage (protected)
    path('', main_views.home, name='home'),

    # ✅ Include your app URLs
    path('players/', include('main.urls')),
]
