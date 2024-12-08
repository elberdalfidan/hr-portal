from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.attendance.models import Attendance, LeaveRequest
from apps.notifications.models import Notification
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from apps.attendance.services.attendance import AttendanceService

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


@login_required
def attendance_records_view(request):
    # Filter by date
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    # User filter (only for admins)
    selected_user_id = request.GET.get('user')
    
    # Base queryset
    queryset = Attendance.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Admin can see all records, employees can only see their own records
    if not request.user.is_superuser:
        queryset = queryset.filter(user=request.user)
    elif selected_user_id:  # Admin can filter by user
        queryset = queryset.filter(user_id=selected_user_id)
    
    # Sorting
    attendance_records = queryset.select_related('user').order_by('-date')
    
    context = {
        'attendance_records': attendance_records,
        'current_year': int(year),
        'current_month': int(month),
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'years': range(timezone.now().year - 2, timezone.now().year + 1),
        'is_admin': request.user.is_superuser,
        'users': User.objects.filter(is_active=True).order_by('first_name', 'last_name') if request.user.is_superuser else None,
        'selected_user_id': int(selected_user_id) if selected_user_id else None
    }
    return render(request, 'dashboard/login_logout_records.html', context)


@login_required
def attendance_records_view(request):
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    selected_user_id = request.GET.get('user')
    
    # Base queryset
    queryset = Attendance.objects.filter(
        date__year=year,
        date__month=month
    )
    
    # Admin can see all records, employees can only see their own records
    if not request.user.is_superuser:
        queryset = queryset.filter(user=request.user)
        monthly_report = AttendanceService.get_monthly_report(request.user, year, month)
        reports = {request.user: monthly_report}
    else:
        if selected_user_id:
            queryset = queryset.filter(user_id=selected_user_id)
            selected_user = User.objects.get(id=selected_user_id)
            monthly_report = AttendanceService.get_monthly_report(selected_user, year, month)
            reports = {selected_user: monthly_report}
        else:
            # All active users' reports
            users = User.objects.filter(is_active=True)
            reports = {
                user: AttendanceService.get_monthly_report(user, year, month)
                for user in users
            }
            monthly_report = None
    
    context = {
        'attendance_records': queryset.select_related('user').order_by('-date'),
        'monthly_report': monthly_report,
        'all_reports': reports,
        'current_year': int(year),
        'current_month': int(month),
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'years': range(timezone.now().year - 2, timezone.now().year + 1),
        'is_admin': request.user.is_superuser,
        'users': User.objects.filter(is_active=True).order_by('first_name', 'last_name') if request.user.is_superuser else None,
        'selected_user_id': int(selected_user_id) if selected_user_id else None
    }
    return render(request, 'dashboard/records.html', context)