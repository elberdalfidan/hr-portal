from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'leave-requests', views.LeaveRequestViewSet, basename='leave-request')

urlpatterns = [
    path('', include(router.urls)),
]

