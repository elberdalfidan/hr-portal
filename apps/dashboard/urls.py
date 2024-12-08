from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='index'),
    path('leave-requests/', views.leave_requests_view, name='leave_requests'),
    path('admin/leave-requests/', views.admin_leave_requests_view, name='admin_leave_requests'),
    path('login-logout-records/', views.attendance_records_view, name='login_logout_records'),
]