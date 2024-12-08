from django.utils import timezone
from django.db.models import F
from datetime import datetime, time
from ..models import Attendance
from apps.notifications.services.notification import NotificationService

class AttendanceService:
    @staticmethod
    def handle_login(user):
        """User login handling"""
        today = timezone.now().date()
        current_time = timezone.now()
        
        attendance, created = Attendance.objects.get_or_create(
            user=user,
            date=today,
            defaults={'first_login': current_time}
        )
        
        if created:
            # Late check
            if current_time.time() > time(8, 0):
                attendance.late_minutes = AttendanceService._calculate_late_minutes(current_time)
                deducted_leave = attendance.calculate_late_deduction()
                
                if deducted_leave > 0:
                    # Leave deduction
                    user.employee.remaining_leave_days = F('remaining_leave_days') - deducted_leave
                    user.employee.save()
                    attendance.deducted_leave = deducted_leave
                    attendance.save()
                    
                    # Notification sending
                    NotificationService.send_late_notification(
                        user=user,
                        late_minutes=attendance.late_minutes,
                        deducted_leave=deducted_leave
                    )
        
        return attendance

    @staticmethod
    def handle_logout(user):
        """User logout handling"""
        today = timezone.now().date()
        current_time = timezone.now()
        
        try:
            attendance = Attendance.objects.get(user=user, date=today)
            attendance.last_logout = current_time
            attendance.save()
            return attendance
        except Attendance.DoesNotExist:
            return None

    @staticmethod
    def _calculate_late_minutes(current_time):
        """Calculate late minutes"""
        work_start = datetime.combine(current_time.date(), time(8, 0))
        return int((current_time - work_start).total_seconds() / 60)

    @staticmethod
    def get_monthly_report(user, year, month):
        """Monthly attendance report"""
        return Attendance.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        ).order_by('date')
