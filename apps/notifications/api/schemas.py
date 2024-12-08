from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.utils import extend_schema, OpenApiExample

class WebSocketSchema:
    """
    WebSocket connection documentation
    """
    
    @staticmethod
    def get_websocket_documentation():
        return {
            "WebSocket Endpoints": {
                "ws://<domain>/ws/notifications/": {
                    "description": "Notification WebSocket connection",
                    "parameters": {
                        "authentication": "JWT token is required"
                    },
                    "messages": {
                        "incoming": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "type": {"type": "string"},
                                "message": {"type": "string"},
                                "created_at": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "example": {
                        "message": {
                            "id": 1,
                            "type": "LATE",
                            "message": "Employee X 30 minutes late",
                            "created_at": "2024-03-08T09:30:00Z"
                        }
                    }
                },
                "ws://<domain>/ws/test/": {
                    "description": "Test WebSocket connection",
                    "messages": {
                        "incoming": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"}
                            }
                        }
                    },
                    "example": {
                        "message": "Test message"
                    }
                }
            }
        }
