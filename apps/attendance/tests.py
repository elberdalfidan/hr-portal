from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from .models import Attendance, LeaveRequest
from datetime import datetime, timedelta

class AttendanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.check_in_url = reverse('attendance-check-in')
        self.check_out_url = reverse('attendance-check-out')

    def test_check_in_success(self):
        response = self.client.post(self.check_in_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        attendance = Attendance.objects.get(user=self.user)
        self.assertIsNotNone(attendance.first_login)
        self.assertIsNone(attendance.last_logout)

    def test_check_out_success(self):
        # First check in
        self.client.post(self.check_in_url)
        
        # Then check out
        response = self.client.post(self.check_out_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        attendance = Attendance.objects.get(user=self.user)
        self.assertIsNotNone(attendance.last_logout)

    def test_calculate_late_deduction(self):
        attendance = Attendance.objects.create(
            user=self.user,
            date=timezone.now().date(),
            first_login=timezone.now().replace(hour=9, minute=30)  # 1.5 hours late
        )
        
        deduction = attendance.calculate_late_deduction()
        self.assertEqual(deduction, 0.15)  # 1.5 hours / 10 hours = 0.15 days

class LeaveRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        self.leave_request_url = reverse('leave-request-list')

    def test_create_leave_request_success(self):
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=2)
        
        response = self.client.post(self.leave_request_url, {
            'start_date': start_date,
            'end_date': end_date,
            'leave_type': 'ANNUAL',
            'reason': 'Vacation'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LeaveRequest.objects.count(), 1)
        
        leave_request = LeaveRequest.objects.first()
        self.assertEqual(leave_request.user, self.user)
        self.assertEqual(leave_request.status, 'PENDING')

    def test_create_leave_request_invalid_dates(self):
        start_date = timezone.now().date()
        end_date = start_date - timedelta(days=1)  # End date before start date
        
        response = self.client.post(self.leave_request_url, {
            'start_date': start_date,
            'end_date': end_date,
            'leave_type': 'ANNUAL',
            'reason': 'Vacation'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_leave_request_invalid_type(self):
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=1)
        
        response = self.client.post(self.leave_request_url, {
            'start_date': start_date,
            'end_date': end_date,
            'leave_type': 'INVALID_TYPE',
            'reason': 'Vacation'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
