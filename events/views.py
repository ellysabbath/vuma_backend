from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from .serializers import EventSerializer

class EventList(APIView):
    permission_classes = []
    
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response({
                'success': True,
                'message': 'Event created successfully',
                'data': EventSerializer(event).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class EventDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            event = Event.objects.get(id=id)
            serializer = EventSerializer(event)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            event = Event.objects.get(id=id)
            serializer = EventSerializer(event, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Event updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            event = Event.objects.get(id=id)
            event.delete()
            return Response({
                'success': True,
                'message': 'Event deleted successfully'
            }, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)

class EventRegisterView(APIView):
    permission_classes = []
    
    def post(self, request, id):
        try:
            event = Event.objects.get(id=id)
            if event.registered < event.capacity:
                event.registered += 1
                event.save()
                return Response({
                    'success': True,
                    'message': f'Successfully registered for {event.title}',
                    'data': EventSerializer(event).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Event is fully booked'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Event not found'
            }, status=status.HTTP_404_NOT_FOUND)