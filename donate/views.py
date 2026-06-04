from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Donation, DonationLog
from .serializers import (
    DonationSerializer, DonationCreateSerializer, 
    DonationUpdateSerializer, DonationStatusUpdateSerializer,
    DonationLogSerializer
)
import logging
import json

logger = logging.getLogger(__name__)


class IsAdminOrReadOnly(IsAdminUser):
    """Custom permission: Admins can do anything, others can only create and view their own"""
    
    def has_permission(self, request, view):
        # Allow POST, OPTIONS, HEAD for creating donations
        if request.method in ['POST', 'OPTIONS', 'HEAD']:
            return True
        # Allow GET for viewing
        if request.method in ['GET']:
            return True
        # Other methods require staff/admin
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Allow GET for anyone
        if request.method in ['GET']:
            return True
        # Other methods require staff/admin
        return request.user and request.user.is_staff


class DonationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Donation CRUD operations
    
    CRUD Operations:
    - GET /api/donations/ - List all donations (admin only)
    - GET /api/donations/{id}/ - Retrieve a donation (public)
    - POST /api/donations/ - Create a new donation (public)
    - PUT /api/donations/{id}/ - Update a donation (admin only)
    - PATCH /api/donations/{id}/ - Partial update (admin only)
    - DELETE /api/donations/{id}/ - Delete a donation (admin only)
    
    Custom Actions:
    - POST /api/donations/{id}/confirm_payment/ - Confirm payment by ID
    - POST /api/donations/status/ - Update status by reference number
    - GET /api/donations/stats/ - Get donation statistics (admin only)
    - GET /api/donations/my_donations/ - Get user's donations by email
    """
    
    queryset = Donation.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'donation_type', 'payment_method']
    search_fields = ['reference_number', 'full_name', 'email', 'mobile_number']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Custom permissions based on action
        - create: AllowAny (public can create donation)
        - list, update, partial_update, destroy: IsAdminUser
        - retrieve: AllowAny (anyone can view by ID)
        """
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['list', 'destroy']:
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [AllowAny]
        elif self.action == 'retrieve':
            permission_classes = [AllowAny]
        elif self.action in ['stats']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DonationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DonationUpdateSerializer
        return DonationSerializer
    
    def perform_create(self, serializer):
        """Save donation with request metadata"""
        donation = serializer.save()
        
        # Log the creation with IP and user agent
        DonationLog.objects.create(
            donation=donation,
            action='created',
            description=f"Donation created online - Amount: {donation.amount} TZS",
            ip_address=self.get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:500]
        )
        
        logger.info(f"New donation created: {donation.reference_number} - {donation.amount} TZS")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny], url_path='confirm-payment')
    def confirm_payment(self, request, pk=None):
        """
        Confirm payment for a specific donation by ID
        POST /api/donations/{id}/confirm-payment/
        """
        donation = self.get_object()
        
        # Log the request for debugging
        logger.info(f"Payment confirmation request for donation ID: {pk}")
        logger.info(f"Request data: {request.data}")
        
        if donation.status == 'completed':
            return Response(
                {
                    'success': False,
                    'error': 'Donation already completed',
                    'status': donation.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method')
        transaction_code = request.data.get('transaction_code')
        
        if not payment_method:
            return Response(
                {
                    'success': False,
                    'error': 'payment_method is required',
                    'allowed_values': ['mpesa', 'bank', 'cash', 'other']
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not transaction_code:
            return Response(
                {
                    'success': False,
                    'error': 'transaction_code is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate payment method
        valid_methods = ['mpesa', 'bank', 'cash', 'other']
        if payment_method not in valid_methods:
            return Response(
                {
                    'success': False,
                    'error': f'Invalid payment_method. Allowed values: {valid_methods}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            donation.mark_as_completed(payment_method, transaction_code)
            
            # Create log entry
            DonationLog.objects.create(
                donation=donation,
                action='payment_confirmed',
                description=f"Payment confirmed via {payment_method} - Transaction: {transaction_code}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            return Response({
                'success': True,
                'message': 'Payment confirmed successfully',
                'reference_number': donation.reference_number,
                'status': donation.status,
                'completed_at': donation.completed_at
            })
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'Failed to confirm payment: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='status')
    def update_status(self, request):
        """
        Update donation status by reference number
        POST /api/donations/status/
        
        Expected payload:
        {
            "reference_number": "VUMA-12345678-001",
            "payment_method": "mpesa",
            "transaction_code": "QRK7L9X2"
        }
        """
        # Log the request for debugging
        logger.info("=" * 50)
        logger.info("Received status update request")
        logger.info(f"Request data: {json.dumps(request.data)}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info("=" * 50)
        
        # Validate serializer
        serializer = DonationStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors,
                    'message': 'Invalid data provided. Please check reference_number, payment_method, and transaction_code.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get validated data
        data = serializer.validated_data
        reference_number = data.get('reference_number')
        payment_method = data.get('payment_method')
        transaction_code = data.get('transaction_code')
        
        logger.info(f"Validated data - Reference: {reference_number}, Method: {payment_method}, Code: {transaction_code}")
        
        try:
            # Find donation by reference number
            donation = Donation.objects.get(reference_number=reference_number)
            logger.info(f"Found donation: {donation.reference_number} - Current status: {donation.status}")
            
            # Check if already completed
            if donation.status == 'completed':
                logger.warning(f"Donation {reference_number} already completed")
                return Response(
                    {
                        'success': False,
                        'error': 'Donation already completed',
                        'status': donation.status,
                        'completed_at': donation.completed_at
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update donation status
            donation.mark_as_completed(payment_method, transaction_code)
            
            # Create log entry
            DonationLog.objects.create(
                donation=donation,
                action='status_updated',
                description=f"Status updated to completed via {payment_method}. Transaction: {transaction_code}",
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            logger.info(f"Donation {reference_number} marked as completed")
            
            return Response({
                'success': True,
                'message': 'Donation status updated successfully',
                'reference_number': donation.reference_number,
                'status': donation.status,
                'completed_at': donation.completed_at,
                'payment_method': donation.payment_method,
                'transaction_code': donation.transaction_code
            })
            
        except Donation.DoesNotExist:
            logger.error(f"Donation not found with reference: {reference_number}")
            return Response(
                {
                    'success': False,
                    'error': f'Donation with reference number "{reference_number}" not found',
                    'message': 'Please check the reference number and try again'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'An unexpected error occurred: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """
        Get donation statistics
        GET /api/donations/stats/
        """
        try:
            # Total counts
            total_donations = Donation.objects.count()
            pending_count = Donation.objects.filter(status='pending').count()
            completed_count = Donation.objects.filter(status='completed').count()
            cancelled_count = Donation.objects.filter(status='cancelled').count()
            
            # Total amount from completed donations
            total_amount = Donation.objects.filter(
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Average donation amount
            avg_amount = Donation.objects.filter(
                status='completed'
            ).aggregate(avg=Sum('amount'))['avg'] or 0
            
            # Monthly statistics for last 6 months
            monthly_stats = Donation.objects.filter(
                status='completed'
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-month')[:6]
            
            # Format monthly stats for response
            formatted_monthly_stats = []
            for stat in monthly_stats:
                formatted_monthly_stats.append({
                    'month': stat['month'].strftime('%B %Y') if stat['month'] else None,
                    'total_amount': int(stat['total']),
                    'total_amount_formatted': f"TZS {int(stat['total']):,}",
                    'count': stat['count']
                })
            
            # Donation type distribution
            one_time_donations = Donation.objects.filter(donation_type='one-time', status='completed').count()
            monthly_donations = Donation.objects.filter(donation_type='monthly', status='completed').count()
            
            # Payment method distribution
            mpesa_payments = Donation.objects.filter(payment_method='mpesa', status='completed').count()
            bank_payments = Donation.objects.filter(payment_method='bank', status='completed').count()
            
            return Response({
                'success': True,
                'total_donations': total_donations,
                'pending_count': pending_count,
                'completed_count': completed_count,
                'cancelled_count': cancelled_count,
                'total_amount': int(total_amount),
                'total_amount_formatted': f"TZS {int(total_amount):,}",
                'average_amount': int(avg_amount) if avg_amount else 0,
                'average_amount_formatted': f"TZS {int(avg_amount):,}" if avg_amount else "TZS 0",
                'donation_type_distribution': {
                    'one_time': one_time_donations,
                    'monthly': monthly_donations
                },
                'payment_method_distribution': {
                    'mpesa': mpesa_payments,
                    'bank': bank_payments
                },
                'monthly_stats': formatted_monthly_stats
            })
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'Failed to retrieve statistics: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='by-email')
    def get_by_email(self, request):
        """
        Get donations by email address (for donors to check their donations)
        GET /api/donations/by-email/?email=user@example.com
        """
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {
                    'success': False,
                    'error': 'email parameter is required',
                    'example': '/api/donations/by-email/?email=john@example.com'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        donations = Donation.objects.filter(email=email).order_by('-created_at')
        serializer = DonationSerializer(donations, many=True)
        
        return Response({
            'success': True,
            'count': donations.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='by-reference')
    def get_by_reference(self, request):
        """
        Get donation by reference number
        GET /api/donations/by-reference/?reference=VUMA-12345678-001
        """
        reference = request.query_params.get('reference')
        
        if not reference:
            return Response(
                {
                    'success': False,
                    'error': 'reference parameter is required',
                    'example': '/api/donations/by-reference/?reference=VUMA-12345678-001'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            donation = Donation.objects.get(reference_number=reference)
            serializer = DonationSerializer(donation)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Donation.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': f'Donation with reference number "{reference}" not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='check-status')
    def check_status(self, request, pk=None):
        """
        Check donation status by ID
        GET /api/donations/{id}/check-status/
        """
        donation = self.get_object()
        
        return Response({
            'success': True,
            'reference_number': donation.reference_number,
            'status': donation.status,
            'amount': int(donation.amount),
            'amount_formatted': f"TZS {int(donation.amount):,}",
            'donation_type': donation.donation_type,
            'created_at': donation.created_at,
            'completed_at': donation.completed_at,
            'payment_method': donation.payment_method,
            'transaction_code': donation.transaction_code
        })


class DonationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing donation logs (admin only)"""
    
    queryset = DonationLog.objects.all()
    serializer_class = DonationLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['donation', 'action']
    search_fields = ['description', 'action']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Allow filtering by donation ID"""
        queryset = super().get_queryset()
        donation_id = self.request.query_params.get('donation_id')
        if donation_id:
            queryset = queryset.filter(donation_id=donation_id)
        return queryset