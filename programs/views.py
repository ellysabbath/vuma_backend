from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Program, Project
from .serializers import ProgramSerializer, ProjectSerializer

class ProgramList(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        programs = Program.objects.all()
        serializer = ProgramSerializer(programs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ProgramSerializer(data=request.data)
        if serializer.is_valid():
            program = serializer.save()
            return Response({
                'success': True,
                'message': 'Program created successfully',
                'data': ProgramSerializer(program).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProgramDetail(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, id):
        try:
            program = Program.objects.get(id=id)
            serializer = ProgramSerializer(program)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Program.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Program not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            program = Program.objects.get(id=id)
            serializer = ProgramSerializer(program, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Program updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Program.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Program not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            program = Program.objects.get(id=id)
            program.delete()
            return Response({
                'success': True,
                'message': 'Program deleted successfully'
            }, status=status.HTTP_200_OK)
        except Program.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Program not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ProjectList(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        projects = Project.objects.all()
        category = request.query_params.get('category', None)
        if category:
            projects = projects.filter(category=category)
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
    permission_classes = [AllowAny]
    
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