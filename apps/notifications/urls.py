from . import views
from django.urls import path

urlpatterns = [
    path('test-websocket-view/', views.test_view, name='test'),
]
