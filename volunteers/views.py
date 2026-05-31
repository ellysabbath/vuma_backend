from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Volunteer
from .serializers import VolunteerSerializer

class VolunteerList(APIView):
    permission_classes = []
    
    def get(self, request):
        volunteers = Volunteer.objects.all()
        serializer = VolunteerSerializer(volunteers, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = VolunteerSerializer(data=request.data)
        if serializer.is_valid():
            volunteer = serializer.save()
            return Response({
                'success': True,
                'message': 'Volunteer created successfully',
                'data': VolunteerSerializer(volunteer).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class VolunteerDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            volunteer = Volunteer.objects.get(id=id)
            serializer = VolunteerSerializer(volunteer)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Volunteer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Volunteer not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            volunteer = Volunteer.objects.get(id=id)
            serializer = VolunteerSerializer(volunteer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Volunteer updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Volunteer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Volunteer not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            volunteer = Volunteer.objects.get(id=id)
            volunteer.delete()
            return Response({
                'success': True,
                'message': 'Volunteer deleted successfully'
            }, status=status.HTTP_200_OK)
        except Volunteer.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Volunteer not found'
            }, status=status.HTTP_404_NOT_FOUND)