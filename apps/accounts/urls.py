from django.urls import path, include
from .views import staff_login_view, admin_login_view

app_name = 'accounts'

urlpatterns = [
    path('staff/login/', staff_login_view, name='staff_login'),
    path('admin/login/', admin_login_view, name='admin_login'),
    path('api/', include('apps.accounts.api.urls')),
]
