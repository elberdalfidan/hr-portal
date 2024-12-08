from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('LATE', 'Late'),
        ('LEAVE_REQUEST', 'Leave Request'),
        ('LEAVE_RESPONSE', 'Leave Response'),
        ('LOW_LEAVE_BALANCE', 'Low Leave Balance'),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    related_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='related_notifications',
        null=True
    )

    class Meta:
        ordering = ['-created_at']
