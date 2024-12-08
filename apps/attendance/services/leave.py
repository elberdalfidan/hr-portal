from django.db.models import F
from ..models import LeaveRequest
from apps.notifications.services.notification import NotificationService
from apps.accounts.models import Employee  # Import here to avoid circular import
from datetime import timedelta

class LeaveRequestService:
    @staticmethod
    def _calculate_working_days(start_date, end_date):
        """Calculate number of working days between two dates, excluding weekends"""
        working_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # 5 = Saturday, 6 = Sunday
            if current_date.weekday() < 5:
                working_days += 1
            current_date += timedelta(days=1)
            
        return working_days

    @staticmethod
    def create_request(user, data):
        """Request leave"""
        # Calculate the number of working days
        requested_days = LeaveRequestService._calculate_working_days(
            data['start_date'],
            data['end_date']
        )
        
        leave_request = LeaveRequest.objects.create(
            user=user,
            start_date=data['start_date'],
            end_date=data['end_date'],
            leave_type=data['leave_type'],
            reason=data['reason'],
            requested_days=requested_days  # Now contains only working days
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

        # If it's an annual leave approval, check leave balance first
        if action == 'APPROVED' and leave_request.leave_type == 'ANNUAL':
            employee = Employee.objects.get(user=leave_request.user)
            if employee.remaining_leave_days < leave_request.requested_days:
                raise ValueError(
                    f"Insufficient leave days. Available: {employee.remaining_leave_days} days, Requested: {leave_request.requested_days} days"
                )
            
            # Update leave balance
            Employee.objects.filter(
                user=leave_request.user
            ).update(
                remaining_leave_days=F('remaining_leave_days') - leave_request.requested_days
            )
            
            # Check if balance is low after update
            if (employee.remaining_leave_days - leave_request.requested_days) <= 3:
                NotificationService.send_low_leave_balance_notification(
                    user=leave_request.user,
                    remaining_days=employee.remaining_leave_days - leave_request.requested_days
                )

        # Update the leave request after successful balance check
        leave_request.status = action
        leave_request.approved_by = admin_user
        leave_request.response_note = note
        leave_request.save()
        
        # Send notification to user
        NotificationService.send_leave_response_notification(
            leave_request=leave_request,
            action=action,
            note=note
        )

    @staticmethod
    def create_admin_request(admin_user, employee_user, data):
        """Admin creates leave request for employee"""
        if not admin_user.is_superuser:
            raise ValueError("Only admin users can create leave requests for employees")

        # Calculate working days
        requested_days = LeaveRequestService._calculate_working_days(
            data['start_date'],
            data['end_date']
        )

        # Get employee record
        try:
            employee = Employee.objects.get(user=employee_user)
        except Employee.DoesNotExist:
            raise ValueError("Employee record not found")

        # Check leave balance for annual leave
        if data['leave_type'] == 'ANNUAL':
            if employee.remaining_leave_days < requested_days:
                raise ValueError(
                    f"Insufficient leave days. Available: {employee.remaining_leave_days} days, "
                    f"Requested: {requested_days} days"
                )

        # Create pre-approved leave request
        leave_request = LeaveRequest.objects.create(
            user=employee_user,
            start_date=data['start_date'],
            end_date=data['end_date'],
            leave_type=data['leave_type'],
            reason=data['reason'],
            requested_days=requested_days,
            status='APPROVED',
            approved_by=admin_user,
            response_note=f"Created by admin {admin_user.first_name} {admin_user.last_name}"
        )

        # Update leave balance for annual leave
        if data['leave_type'] == 'ANNUAL':
            employee.remaining_leave_days -= requested_days
            employee.save()

        # Send notification to employee
        NotificationService.send_leave_response_notification(
            leave_request=leave_request,
            action='APPROVED',
            note="Created by admin"
        )

        return leave_request
