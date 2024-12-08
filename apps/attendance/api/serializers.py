from rest_framework import serializers
from ..models import Attendance, LeaveRequest

class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'user_name', 'date', 'first_login', 
            'last_logout', 'late_minutes', 'deducted_leave'
        ]
        read_only_fields = ['deducted_leave']

class LeaveRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'user', 'user_name', 'start_date', 'end_date',
            'leave_type', 'reason', 'status', 'status_display',
            'requested_days', 'response_note', 'created_at'
        ]
        read_only_fields = ['status', 'response_note']

class LeaveRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'response_note']

class MonthlyReportSerializer(serializers.Serializer):
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    total_late_minutes = serializers.IntegerField()
    total_deducted_leave = serializers.DecimalField(max_digits=4, decimal_places=2)
