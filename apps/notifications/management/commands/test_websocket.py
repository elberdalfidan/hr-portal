from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test WebSocket connections'

    def handle(self, *args, **kwargs):
        try:
            # Redis connection test
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_add)("test_group", "test_channel")
            
            # Send test message
            async_to_sync(channel_layer.group_send)(
                "test_group",
                {
                    "type": "test.message",
                    "message": "Test successful!"
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS('WebSocket connection successful!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
