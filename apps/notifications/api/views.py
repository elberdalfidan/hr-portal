from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from ..models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for notification operations
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List notifications",
        description="Lists all notifications for the user",
        responses={200: NotificationSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get notification details",
        description="Shows details of a specific notification",
        responses={200: NotificationSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Mark notification as read",
        description="Marks a specific notification as read",
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'marked as read'})

    @extend_schema(
        summary="Mark all notifications as read",
        description="Marks all notifications for the user as read",
        responses={200: {"type": "object", "properties": {"status": {"type": "string"}}}}
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().filter(read_at__isnull=True).update(
            read_at=timezone.now()
        )
        return Response({'status': 'all marked as read'})

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
