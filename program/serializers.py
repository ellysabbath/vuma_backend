from rest_framework import serializers
from .models import Program, Activity, Explanation

class ExplanationSerializer(serializers.ModelSerializer):
    """Serializer for Explanation model"""
    
    class Meta:
        model = Explanation
        fields = [
            'id', 'activity', 'title', 'content', 'explanation_type', 
            'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model with nested explanations"""
    explanations = ExplanationSerializer(many=True, read_only=True)
    explanation_count = serializers.IntegerField(source='explanations.count', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'program', 'name', 'description', 'icon', 'duration', 
            'target_audience', 'max_participants', 'order', 'is_active',
            'explanations', 'explanation_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model with nested activities"""
    activities = ActivitySerializer(many=True, read_only=True)
    activity_count = serializers.IntegerField(source='activities.count', read_only=True)
    
    class Meta:
        model = Program
        fields = [
            'id', 'name', 'category', 'description', 'icon', 'color', 
            'order', 'is_active', 'activities', 'activity_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============== CREATE/UPDATE SERIALIZERS WITH NESTED WRITING ==============

class ExplanationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating explanations"""
    
    class Meta:
        model = Explanation
        fields = ['id', 'activity', 'title', 'content', 'explanation_type', 'order']


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating activities with nested explanations"""
    explanations = ExplanationCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'program', 'name', 'description', 'icon', 'duration', 
            'target_audience', 'max_participants', 'order', 'is_active', 'explanations'
        ]
    
    def create(self, validated_data):
        explanations_data = validated_data.pop('explanations', [])
        activity = Activity.objects.create(**validated_data)
        
        for explanation_data in explanations_data:
            Explanation.objects.create(activity=activity, **explanation_data)
        
        return activity
    
    def update(self, instance, validated_data):
        explanations_data = validated_data.pop('explanations', None)
        
        # Update activity fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle explanations if provided
        if explanations_data is not None:
            # Clear existing explanations and create new ones
            instance.explanations.all().delete()
            for explanation_data in explanations_data:
                Explanation.objects.create(activity=instance, **explanation_data)
        
        return instance


class ProgramCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating programs with nested activities and explanations"""
    activities = ActivityCreateUpdateSerializer(many=True, required=False)
    
    class Meta:
        model = Program
        fields = [
            'id', 'name', 'category', 'description', 'icon', 'color', 
            'order', 'is_active', 'activities'
        ]
    
    def create(self, validated_data):
        activities_data = validated_data.pop('activities', [])
        program = Program.objects.create(**validated_data)
        
        for activity_data in activities_data:
            explanations_data = activity_data.pop('explanations', [])
            activity = Activity.objects.create(program=program, **activity_data)
            
            for explanation_data in explanations_data:
                Explanation.objects.create(activity=activity, **explanation_data)
        
        return program
    
    def update(self, instance, validated_data):
        activities_data = validated_data.pop('activities', None)
        
        # Update program fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle activities if provided
        if activities_data is not None:
            # Clear existing activities and explanations
            instance.activities.all().delete()
            
            for activity_data in activities_data:
                explanations_data = activity_data.pop('explanations', [])
                activity = Activity.objects.create(program=instance, **activity_data)
                
                for explanation_data in explanations_data:
                    Explanation.objects.create(activity=activity, **explanation_data)
        
        return instance


class ProgramListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    activity_count = serializers.IntegerField(source='activities.count', read_only=True)
    
    class Meta:
        model = Program
        fields = ['id', 'name', 'category', 'description', 'icon', 'color', 'activity_count', 'is_active']