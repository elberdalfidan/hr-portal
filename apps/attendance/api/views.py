from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models import Attendance, LeaveRequest
from ..services.attendance import AttendanceService
from ..services.leave import LeaveRequestService
from .serializers import (
    AttendanceSerializer,
    LeaveRequestSerializer,
    LeaveRequestUpdateSerializer,
    MonthlyReportSerializer
)

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Attendance.objects.all()
        return Attendance.objects.filter(user=user)

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        attendance = AttendanceService.handle_login(request.user)
        return Response(
            AttendanceSerializer(attendance).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        attendance = AttendanceService.handle_logout(request.user)
        if attendance:
            return Response(
                AttendanceSerializer(attendance).data,
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'No active attendance found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        
        report = AttendanceService.get_monthly_report(request.user, year, month)
        return Response(MonthlyReportSerializer(report).data)

class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        LeaveRequestService.create_request(
            user=self.request.user,
            data=serializer.validated_data
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        leave_request = self.get_object()
        serializer = LeaveRequestUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            LeaveRequestService.process_request(
                leave_request=leave_request,
                admin_user=request.user,
                action='APPROVED',
                note=serializer.validated_data.get('response_note')
            )
            return Response({'status': 'approved'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        leave_request = self.get_object()
        serializer = LeaveRequestUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            LeaveRequestService.process_request(
                leave_request=leave_request,
                admin_user=request.user,
                action='REJECTED',
                note=serializer.validated_data.get('response_note')
            )
            return Response({'status': 'rejected'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
