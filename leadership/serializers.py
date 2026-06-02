from rest_framework import serializers
from .models import Leader, Project, Testimonial, BlogPost, Statistic
import base64
import re

class Base64ImageSerializerMixin:
    """Mixin to handle base64 image decoding/encoding"""
    
    def validate_image_base64(self, value):
        """Validate and process base64 image"""
        if not value:
            return value
        
        # Check if it's a valid base64 data URL string
        if isinstance(value, str):
            # Validate base64 data URL format
            if value.startswith('data:image'):
                # Extract extension from mime type
                format_match = re.match(r'data:image/(\w+);base64,', value)
                if format_match:
                    ext = format_match.group(1).lower()
                    # Validate image format
                    if ext not in ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp']:
                        raise serializers.ValidationError(
                            f"Unsupported image format: {ext}. Supported: jpeg, jpg, png, gif, webp, bmp"
                        )
                    return value
                else:
                    raise serializers.ValidationError("Invalid base64 image format")
            else:
                raise serializers.ValidationError("Image must be a base64 data URL")
        
        return value

class LeaderSerializer(serializers.ModelSerializer, Base64ImageSerializerMixin):
    class Meta:
        model = Leader
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image_base64:
            # Return the full data URL
            representation['image_url'] = instance.get_image_html()
        else:
            representation['image_url'] = None
        return representation

class ProjectSerializer(serializers.ModelSerializer, Base64ImageSerializerMixin):
    class Meta:
        model = Project
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image_base64:
            representation['image_url'] = instance.get_image_html()
        else:
            representation['image_url'] = None
        return representation

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class BlogPostSerializer(serializers.ModelSerializer, Base64ImageSerializerMixin):
    class Meta:
        model = BlogPost
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image_base64:
            representation['image_url'] = instance.get_image_html()
        else:
            representation['image_url'] = None
        return representation

class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = '__all__'