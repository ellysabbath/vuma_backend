from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Program, Activity, Explanation
from .serializers import (
    ProgramSerializer, ProgramCreateUpdateSerializer, ProgramListSerializer,
    ActivitySerializer, ActivityCreateUpdateSerializer,
    ExplanationSerializer, ExplanationCreateUpdateSerializer
)


class ProgramViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Program CRUD operations
    No permission classes - fully open
    """
    queryset = Program.objects.all()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return ProgramCreateUpdateSerializer
        elif self.action == 'list':
            return ProgramListSerializer
        return ProgramSerializer
    
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get all activities for a specific program"""
        program = self.get_object()
        activities = program.activities.all()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_activity(self, request, pk=None):
        """Add a new activity to a program"""
        program = self.get_object()
        serializer = ActivityCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(program=program)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get programs grouped by category"""
        categories = Program.PROGRAM_CATEGORIES
        result = {}
        for category_key, category_name in categories:
            programs = Program.objects.filter(category=category_key, is_active=True)
            serializer = ProgramSerializer(programs, many=True)
            result[category_key] = {
                'name': category_name,
                'programs': serializer.data
            }
        return Response(result)


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity CRUD operations
    No permission classes - fully open
    """
    queryset = Activity.objects.all()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return ActivityCreateUpdateSerializer
        return ActivitySerializer
    
    @action(detail=True, methods=['get'])
    def explanations(self, request, pk=None):
        """Get all explanations for a specific activity"""
        activity = self.get_object()
        explanations = activity.explanations.all()
        serializer = ExplanationSerializer(explanations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_explanation(self, request, pk=None):
        """Add a new explanation to an activity"""
        activity = self.get_object()
        serializer = ExplanationCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(activity=activity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_program(self, request):
        """Get activities filtered by program"""
        program_id = request.query_params.get('program_id')
        if program_id:
            activities = Activity.objects.filter(program_id=program_id, is_active=True)
            serializer = ActivitySerializer(activities, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'program_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ExplanationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Explanation CRUD operations
    No permission classes - fully open
    """
    queryset = Explanation.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ExplanationCreateUpdateSerializer
        return ExplanationSerializer
    
    @action(detail=False, methods=['get'])
    def by_activity(self, request):
        """Get explanations filtered by activity"""
        activity_id = request.query_params.get('activity_id')
        if activity_id:
            explanations = Explanation.objects.filter(activity_id=activity_id)
            serializer = ExplanationSerializer(explanations, many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'activity_id parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )