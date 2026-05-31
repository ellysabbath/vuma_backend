from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer

class NewsList(APIView):
    permission_classes = []
    
    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            news = serializer.save()
            return Response({
                'success': True,
                'message': 'News created successfully',
                'data': NewsSerializer(news).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class NewsDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.views += 1
            news.save()
            serializer = NewsSerializer(news)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            news = News.objects.get(id=id)
            serializer = NewsSerializer(news, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'News updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.delete()
            return Response({
                'success': True,
                'message': 'News deleted successfully'
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)

class NewsLikeView(APIView):
    permission_classes = []
    
    def post(self, request, id):
        try:
            news = News.objects.get(id=id)
            news.likes += 1
            news.save()
            return Response({
                'success': True,
                'message': 'News liked successfully',
                'likes': news.likes
            }, status=status.HTTP_200_OK)
        except News.DoesNotExist:
            return Response({
                'success': False,
                'error': 'News not found'
            }, status=status.HTTP_404_NOT_FOUND)