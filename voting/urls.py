from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Voting
    path('vote/<int:election_id>/', views.voting_page, name='voting_page'),
    path('results/<int:election_id>/', views.results_view, name='results'),
    
    # API
    path('api/time-left/<int:election_id>/', views.election_time_left, name='time_left'),
    
    # Admin
     path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/create-election/', views.create_election, name='create_election'),
    path('admin/add-candidate/<int:election_id>/', views.add_candidate, name='add_candidate'),
    path('admin/toggle-election/<int:election_id>/', views.toggle_election, name='toggle_election'),
]