from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upload-voters/', views.upload_voters, name='upload_voters'),
    path('voter-success/', views.voter_success, name='voter_success'),
    path('admin/manage-candidates/', views.manage_candidates, name='manage_candidates'),
    path('admin/manage-candidates/delete/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),
    path('start-stop-election/', views.start_stop_election, name='start_stop_election'),
    path('results/', views.view_results, name='view_results'),
    path('logs/', views.logs, name='logs'),
    path('system-settings/', views.system_settings, name='system_settings'),
    path('login/', views.voter_authentication, name='voter_authentication'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('face-verification/', views.face_verification, name='face_verification'),
    path('voting/', views.voting_page, name='voting_page'),
    path('vote-success/', views.vote_success, name='vote_success'),
]