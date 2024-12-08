from django.utils import timezone
from ..models import LeaveRequest
from apps.notifications.services.notification import NotificationService

class LeaveRequestService:
    @staticmethod
    def create_request(user, data):
        """Request leave"""
        leave_request = LeaveRequest.objects.create(
            user=user,
            start_date=data['start_date'],
            end_date=data['end_date'],
            leave_type=data['leave_type'],
            reason=data['reason']
        )
        
        # Send notification to admins
        NotificationService.send_leave_request_notification(
            requesting_user=user,
            leave_request=leave_request
        )
        
        return leave_request

    @staticmethod
    def process_request(leave_request, admin_user, action, note=None):
        """Approve/reject leave request"""
        if action not in ['APPROVED', 'REJECTED']:
            raise ValueError("Invalid action")
            
        leave_request.status = action
        leave_request.approved_by = admin_user
        leave_request.response_note = note
        leave_request.save()
        
        if action == 'APPROVED' and leave_request.leave_type == 'ANNUAL':
            # Deduct leave days
            employee = leave_request.user.employee
            employee.remaining_leave_days -= leave_request.requested_days
            employee.save()
            
            # Low leave balance check
            if employee.remaining_leave_days <= 3:
                NotificationService.send_low_leave_balance_notification(
                    user=leave_request.user,
                    remaining_days=employee.remaining_leave_days
                )
        
        # Send notification to user
        NotificationService.send_leave_response_notification(
            leave_request=leave_request,
            action=action,
            note=note
        )
