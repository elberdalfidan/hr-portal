from django.urls import path
from . import views

urlpatterns = [
    path('staff/login/', views.StaffLoginAPIView.as_view(), name='staff_login_api'),
    path('admin/login/', views.AdminLoginAPIView.as_view(), name='admin_login_api'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout_api'),

    path('employees/', views.get_employees, name='get_employees_api'),
]
