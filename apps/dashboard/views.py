from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.attendance.models import Attendance, LeaveRequest
from apps.notifications.models import Notification

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    
    context = {
        # Today's attendance status
        'today_attendance': Attendance.objects.filter(
            user=request.user,
            date=today
        ).first(),
        
        # Last 5 notifications
        'recent_notifications': Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5],
        
        # Active leave requests (Pending and approved)
        'active_leave_requests': LeaveRequest.objects.filter(
            user=request.user,
            status__in=['PENDING', 'APPROVED'],
            end_date__gte=today
        ).order_by('start_date')[:5],
    }
    
    return render(request, 'dashboard/index.html', context)