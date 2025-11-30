from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from lottery.models import Raffle
from api.lottery.serializers import RaffleSerializer
from .services import update_raffle_start_time
from .serializers import (
    CRMLoginSerializer,
    UpdateRaffleStartTimeSerializer,
    RaffleStartTimeUpdateResponseSerializer
)


class CRMLoginView(APIView):
    """
    POST /api/crm/auth/login/
    
    Authenticates admin user with username and password.
    Only users with is_staff=True or is_superuser=True can access CRM.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CRMLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is staff/admin
        if not user.is_staff and not user.is_superuser:
            return Response(
                {"detail": "Access denied. Admin privileges required."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is active
        if not user.is_active:
            return Response(
                {"detail": "User account is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        })


class CRMUserView(APIView):
    """
    GET /api/crm/auth/me/
    
    Returns current authenticated user information.
    Used to verify token validity on page load.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })


class RaffleListForCRMView(ListAPIView):
    """
    GET /api/crm/raffles/
    
    Returns list of all raffles (including finished ones) for CRM management.
    """
    serializer_class = RaffleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return all raffles for CRM management."""
        return Raffle.objects.select_related('prize', 'type').prefetch_related('entries').order_by('-created_at')


class RaffleDetailForCRMView(APIView):
    """
    GET /api/crm/raffles/<raffle_id>/
    
    Returns detailed raffle information for CRM.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, raffle_id):
        raffle = get_object_or_404(
            Raffle.objects.select_related('prize', 'type').prefetch_related('entries'),
            id=raffle_id
        )
        serializer = RaffleSerializer(raffle)
        return Response(serializer.data)


class UpdateRaffleStartTimeView(APIView):
    """
    POST /api/crm/raffles/<raffle_id>/update-start-time/
    
    Updates raffle start time and reschedules associated task.
    
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, raffle_id):
        """
        Update raffle start time.
        
        Request body:
        {
            "new_start_at": "2025-12-05T10:00:00Z"
        }
        """
        # Get raffle
        raffle = get_object_or_404(Raffle, id=raffle_id)
        
        # Validate request data
        serializer = UpdateRaffleStartTimeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_start_at = serializer.validated_data['new_start_at']
        
        try:
            # Update raffle start time and reschedule task
            result = update_raffle_start_time(raffle, new_start_at)
            
            # Prepare response
            response_data = {
                'raffle_id': raffle.id,
                'raffle_name': raffle.name,
                'old_start_at': result['old_start_at'],
                'new_start_at': result['new_start_at'],
                'task_rescheduled': result['task_rescheduled'],
                'task_info': result.get('task_info'),
                'message': (
                    f"Raffle start time updated successfully. "
                    f"Task {'rescheduled' if result['task_rescheduled'] else 'not found or already completed'}."
                )
            }
            
            response_serializer = RaffleStartTimeUpdateResponseSerializer(data=response_data)
            response_serializer.is_valid()  # This will always be valid since we constructed it
            
            return Response(
                response_serializer.validated_data,
                status=status.HTTP_200_OK
            )
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
