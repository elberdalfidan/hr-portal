from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from ..models import Notification
from django.utils import timezone

class NotificationService:
    @staticmethod
    def create_notification(recipient, notification_type, message, related_user=None):
        """Create notification and send via WebSocket"""
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            message=message,
            related_user=related_user
        )
        
        # Send via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient.id}_notifications",
            {
                "type": "notification_message",
                "message": {
                    "id": notification.id,
                    "type": notification_type,
                    "message": message,
                    "created_at": notification.created_at.isoformat()
                }
            }
        )
        
        return notification

    @staticmethod
    def send_late_notification(user, late_minutes, deducted_leave):
        """Late notification"""
        admin_users = User.objects.filter(is_superuser=True)
        
        for admin in admin_users:
            NotificationService.create_notification(
                recipient=admin,
                notification_type='LATE',
                message=f"{user.get_full_name()} {late_minutes} dakika geç kaldı. ({deducted_leave} gün kesinti)",
                related_user=user
            )

    @staticmethod
    def send_leave_request_notification(requesting_user, leave_request):
        """Leave request notification"""
        admin_users = User.objects.filter(is_superuser=True)
        
        for admin in admin_users:
            NotificationService.create_notification(
                recipient=admin,
                notification_type='LEAVE_REQUEST',
                message=f"{requesting_user.get_full_name()} {leave_request.requested_days} gün izin talep etti.",
                related_user=requesting_user
            )

    @staticmethod
    def send_leave_response_notification(leave_request, action, note=None):
        """Leave response notification"""
        message = f"Your leave request is {leave_request.get_status_display().lower()}"
        if note:
            message += f": {note}"
            
        NotificationService.create_notification(
            recipient=leave_request.user,
            notification_type='LEAVE_RESPONSE',
            message=message,
            related_user=leave_request.approved_by
        )

    @staticmethod
    def send_low_leave_balance_notification(user, remaining_days):
        """Low leave balance notification"""
        admin_users = User.objects.filter(is_superuser=True)
        
        for admin in admin_users:
            NotificationService.create_notification(
                recipient=admin,
                notification_type='LOW_LEAVE_BALANCE',
                message=f"User {user.get_full_name()} has {remaining_days} days left",
                related_user=user
            )
