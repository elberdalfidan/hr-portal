from django.utils import timezone
from django.db.models import F, ExpressionWrapper, fields, Count, Case, When, Sum
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
        work_start = timezone.make_aware(
            datetime.combine(current_time.date(), time(8, 0))
        )
        if current_time <= work_start:
            return 0
            
        late_duration = current_time - work_start
        return int(late_duration.total_seconds() / 60)

    @staticmethod
    def get_monthly_report(user, year, month):
        """Monthly attendance report"""
        records = Attendance.objects.filter(
            user=user,
            date__year=year,
            date__month=month
        )
        
        # Work hours calculation
        work_hours = records.annotate(
            work_duration=ExpressionWrapper(
                F('last_logout') - F('first_login'),
                output_field=fields.DurationField()
            )
        ).aggregate(
            total_days=Count('id'),
            present_days=Count(Case(When(first_login__isnull=False, then=1))),
            absent_days=Count(Case(When(first_login__isnull=True, then=1))),
            late_days=Count(Case(When(late_minutes__gt=0, then=1))),
            total_late_minutes=Sum('late_minutes'),
            total_work_hours=Sum('work_duration', output_field=fields.DurationField()),
            total_deducted_leave=Sum('deducted_leave')
        )
        
        # None values to 0
        work_hours = {k: v or 0 for k, v in work_hours.items()}
        
        # Convert total work hours to hours
        if work_hours['total_work_hours']:
            total_hours = work_hours['total_work_hours'].total_seconds() / 3600
            work_hours['total_work_hours'] = round(total_hours, 2)
        else:
            work_hours['total_work_hours'] = 0
            
        # Average daily work hours
        if work_hours['present_days']:
            work_hours['average_daily_hours'] = round(
                work_hours['total_work_hours'] / work_hours['present_days'], 
                2
            )
        else:
            work_hours['average_daily_hours'] = 0
            
        return work_hours
