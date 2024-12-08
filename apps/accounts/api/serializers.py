from rest_framework import serializers
from django.contrib.auth.models import User

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'is_staff', 'is_superuser']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username