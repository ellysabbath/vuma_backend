from rest_framework import serializers
from .models import Donation, DonationLog

class DonationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationLog
        fields = ['id', 'action', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class DonationSerializer(serializers.ModelSerializer):
    logs = DonationLogSerializer(many=True, read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Donation
        fields = [
            'id', 'reference_number', 'donation_type', 'amount', 'formatted_amount',
            'full_name', 'email', 'mobile_number', 'location', 'message',
            'status', 'payment_method', 'transaction_code',
            'created_at', 'updated_at', 'completed_at', 'admin_notes', 'logs'
        ]
        read_only_fields = [
            'id', 'reference_number', 'created_at', 'updated_at', 
            'completed_at', 'formatted_amount', 'logs'
        ]
    
    def get_formatted_amount(self, obj):
        """Return formatted currency"""
        return f"TZS {int(obj.amount):,}"
    
    def validate_amount(self, value):
        """Validate minimum donation amount"""
        if value < 1000:
            raise serializers.ValidationError("Minimum donation amount is 1,000 TZS")
        return value
    
    def validate_mobile_number(self, value):
        """Validate mobile number format"""
        import re
        if not re.match(r'^[0-9]{10,15}$', value.replace('+', '').replace(' ', '')):
            raise serializers.ValidationError("Invalid mobile number format")
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email address")
        return value


class DonationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating donations (no read-only fields required)"""
    
    class Meta:
        model = Donation
        fields = [
            'donation_type', 'amount', 'full_name', 'email', 
            'mobile_number', 'location', 'message'
        ]
    
    def validate_amount(self, value):
        if value < 1000:
            raise serializers.ValidationError("Minimum donation amount is 1,000 TZS")
        return value
    
    def create(self, validated_data):
        donation = Donation.objects.create(**validated_data)
        
        # Create log entry
        DonationLog.objects.create(
            donation=donation,
            action='created',
            description=f"Donation created with reference {donation.reference_number}"
        )
        
        return donation


class DonationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating donation status"""
    
    class Meta:
        model = Donation
        fields = ['status', 'payment_method', 'transaction_code', 'admin_notes']
    
    def update(self, instance, validated_data):
        old_status = instance.status
        instance = super().update(instance, validated_data)
        
        # Create log entry for status change
        if old_status != instance.status:
            DonationLog.objects.create(
                donation=instance,
                action='status_changed',
                description=f"Status changed from {old_status} to {instance.status}"
            )
        
        # If marked as completed, set completed_at
        if instance.status == 'completed' and not instance.completed_at:
            from django.utils import timezone
            instance.completed_at = timezone.now()
            instance.save()
            
            DonationLog.objects.create(
                donation=instance,
                action='completed',
                description=f"Donation completed via {instance.payment_method} - Transaction: {instance.transaction_code}"
            )
        
        return instance


class DonationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating payment status"""
    payment_method = serializers.CharField(max_length=100, required=True)
    transaction_code = serializers.CharField(max_length=100, required=True)
    reference_number = serializers.CharField(max_length=50, required=False)
    
    def validate_reference_number(self, value):
        try:
            donation = Donation.objects.get(reference_number=value)
            if donation.status == 'completed':
                raise serializers.ValidationError("This donation is already completed")
            return value
        except Donation.DoesNotExist:
            raise serializers.ValidationError(f"Donation with reference {value} not found")