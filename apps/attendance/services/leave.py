from django.db.models import F
from ..models import LeaveRequest
from apps.notifications.services.notification import NotificationService
from apps.accounts.models import Employee  # Import here to avoid circular import

class LeaveRequestService:
    @staticmethod
    def create_request(user, data):
        """Request leave"""
        # Calculate the number of days
        requested_days = (data['end_date'] - data['start_date']).days + 1
        
        leave_request = LeaveRequest.objects.create(
            user=user,
            start_date=data['start_date'],
            end_date=data['end_date'],
            leave_type=data['leave_type'],
            reason=data['reason'],
            requested_days=requested_days  # Add the calculated number of days
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
            
        if leave_request.status != 'PENDING':
            raise ValueError("This request has already been processed")

        # Update the leave request
        leave_request.status = action
        leave_request.approved_by = admin_user
        leave_request.response_note = note
        leave_request.save()
        
        # If approved and annual leave, deduct leave days
        if action == 'APPROVED' and leave_request.leave_type == 'ANNUAL':
            # Direct update with filter
            updated = Employee.objects.filter(
                user=leave_request.user,
                remaining_leave_days__gte=leave_request.requested_days
            ).update(
                remaining_leave_days=F('remaining_leave_days') - leave_request.requested_days
            )
            
            if not updated:
                raise ValueError(
                    f"Insufficient leave days. Requested: {leave_request.requested_days} days"
                )
            
            # Get the current remaining leave days
            employee = Employee.objects.get(user=leave_request.user)
            
            # Send low leave balance notification if remaining leave days are less than or equal to 3
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
