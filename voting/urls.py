from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('main/', views.home, name='main'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),

    # Voter Dashboard
    path('public-dashboard/', views.public_dashboard, name='public_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('voter/', views.voter_portal, name='voter_portal'),
    path('voter-education/', views.voter_education, name='voter_education'),
    path('admin-portal/', views.admin_portal, name='admin_portal'),
    path('profile/', views.profile, name='profile'),
    path('statistics/', views.voter_statistics, name='voter_statistics'),

    # Voting URLs
    path('vote/<str:position>/', views.vote, name='vote'),
    path('confirm-vote/<int:candidate_id>/<str:position>/',
         views.confirm_vote, name='confirm_vote'),
    path('vote-success/', views.vote_success, name='vote_success'),

    # Ajax endpoints for dependent dropdowns
    path('load-constituencies/', views.load_constituencies,
         name='load_constituencies'),
    path('load-wards/', views.load_wards, name='load_wards'),
    path('load-polling-centers/', views.load_polling_centers,
         name='load_polling_centers'),
    path('load-polling-stations/', views.load_polling_stations,
         name='load_polling_stations'),

    # Admin Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('election-statistics/', views.election_statistics,
         name='election_statistics'),
]
