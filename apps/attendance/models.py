from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time

class Attendance(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(default=timezone.now)
    first_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    late_minutes = models.PositiveIntegerField(default=0)
    deducted_leave = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0,
        help_text="Geç kalma nedeniyle kesilen izin günü"
    )

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def calculate_late_deduction(self):
        """
        Calculate the deduction for late minutes. (600 minutes = 1 day)
        """
        if not self.first_login:
            return 0
        
        expected_time = datetime.combine(self.date, time(8,0))
        actual_time = self.first_login

        if actual_time <= expected_time:
            return 0
        
        late_duration = actual_time - expected_time
        late_hours = late_duration.total_seconds() / 3600
        return round(late_hours / 10, 2)
    
class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )    

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(
        max_length=20,
        choices=(
            ('ANNUAL', 'Annual'),
            ('SICK', 'Sick'),
            ('OTHER', 'Other'),
        ),
        default='ANNUAL'
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    requested_days = models.DecimalField(max_digits=4, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    response_note = models.TextField(null=True, blank=True)

