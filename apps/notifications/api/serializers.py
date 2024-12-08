from rest_framework import serializers
from ..models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    related_user_name = serializers.CharField(
        source='related_user.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'message', 
            'created_at', 'read_at', 'related_user_name'
        ]
