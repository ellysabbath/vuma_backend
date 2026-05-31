from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .models import Project
from .serializers import ProjectSerializer

class ProjectList(APIView):
    permission_classes = []
    
    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response({
                'success': True,
                'message': 'Project created successfully',
                'data': ProjectSerializer(project).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            project = Project.objects.get(id=id)
            serializer = ProjectSerializer(project)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            project = Project.objects.get(id=id)
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Project updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            project = Project.objects.get(id=id)
            project.delete()
            return Response({
                'success': True,
                'message': 'Project deleted successfully'
            }, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)

class ProjectStatsView(APIView):
    permission_classes = []
    
    def get(self, request):
        total_projects = Project.objects.count()
        ongoing_projects = Project.objects.filter(status='Ongoing').count()
        completed_projects = Project.objects.filter(status='Completed').count()
        planning_projects = Project.objects.filter(status='Planning').count()
        
        environment_projects = Project.objects.filter(category='Environment').count()
        leadership_projects = Project.objects.filter(category='Leadership').count()
        
        avg_progress = Project.objects.aggregate(avg=models.Avg('progress'))['avg'] or 0
        
        return Response({
            'success': True,
            'data': {
                'total': total_projects,
                'ongoing': ongoing_projects,
                'completed': completed_projects,
                'planning': planning_projects,
                'environment': environment_projects,
                'leadership': leadership_projects,
                'avg_progress': round(avg_progress, 1)
            }
        }, status=status.HTTP_200_OK)