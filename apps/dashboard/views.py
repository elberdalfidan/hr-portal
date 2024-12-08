from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.attendance.models import Attendance, LeaveRequest
from apps.notifications.models import Notification
from django.contrib.auth.decorators import user_passes_test
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


@login_required
def leave_requests_view(request):
    # User's leave requests
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
    }
    return render(request, 'dashboard/leave_requests.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_leave_requests_view(request):
    # All leave requests
    leave_requests = LeaveRequest.objects.all().order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
    }
    return render(request, 'dashboard/admin_leave_requests.html', context)