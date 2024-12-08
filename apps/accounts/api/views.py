from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from .serializers import UserLoginSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.attendance.services.attendance import AttendanceService

class StaffLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    

    @extend_schema(
        tags=['auth'],
        operation_id='staff_login',
        description='Login endpoint for staff members',
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Login successful',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'},
                        'user': {'type': 'object'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='Invalid credentials',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'error'},
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user and user.is_staff and not user.is_superuser:
                login(request, user)

                # Save login record
                AttendanceService.handle_login(user)

                return Response({
                    'status': 'success',
                    'user': UserSerializer(user).data
                })
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials or insufficient permissions'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        tags=['auth'],
        operation_id='admin_login',
        description='Login endpoint for admin users',
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                description='Login successful',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'},
                        'user': {'type': 'object'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='Invalid credentials',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'error'},
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)

            if user and user.is_superuser:
                login(request, user)
                return Response({
                    'status': 'success',
                    'user': UserSerializer(user).data
                })
            
            return Response({
                'status': 'error',
                'message': 'Invalid credentials or insufficient permissions'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    @extend_schema(
        tags=['auth'],
        operation_id='logout',
        description='Logout endpoint for all users',
        responses={
            200: OpenApiResponse(
                description='Logout successful',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'}
                    }
                }
            )
        }
    )
    def post(self, request):
        AttendanceService.handle_logout(request.user)
        logout(request)
        return Response({'status': 'success'})

