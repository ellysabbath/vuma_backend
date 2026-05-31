from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Partner
from .serializers import PartnerSerializer

class PartnerList(APIView):
    permission_classes = []
    
    def get(self, request):
        partners = Partner.objects.all()
        partner_type = request.query_params.get('type', None)
        status_filter = request.query_params.get('status', None)
        
        if partner_type:
            partners = partners.filter(type=partner_type)
        if status_filter:
            partners = partners.filter(status=status_filter)
            
        serializer = PartnerSerializer(partners, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PartnerSerializer(data=request.data)
        if serializer.is_valid():
            partner = serializer.save()
            return Response({
                'success': True,
                'message': 'Partner created successfully',
                'data': PartnerSerializer(partner).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class PartnerDetail(APIView):
    permission_classes = []
    
    def get(self, request, id):
        try:
            partner = Partner.objects.get(id=id)
            serializer = PartnerSerializer(partner)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Partner.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Partner not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            partner = Partner.objects.get(id=id)
            serializer = PartnerSerializer(partner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Partner updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Partner.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Partner not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        try:
            partner = Partner.objects.get(id=id)
            partner.delete()
            return Response({
                'success': True,
                'message': 'Partner deleted successfully'
            }, status=status.HTTP_200_OK)
        except Partner.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Partner not found'
            }, status=status.HTTP_404_NOT_FOUND)

class PartnerStatsView(APIView):
    permission_classes = []
    
    def get(self, request):
        total_partners = Partner.objects.count()
        active_partners = Partner.objects.filter(status='active').count()
        pending_partners = Partner.objects.filter(status='pending').count()
        
        development_partners = Partner.objects.filter(type='development').count()
        environmental_partners = Partner.objects.filter(type='environmental').count()
        corporate_partners = Partner.objects.filter(type='corporate').count()
        ngo_partners = Partner.objects.filter(type='ngo').count()
        
        return Response({
            'success': True,
            'data': {
                'total': total_partners,
                'active': active_partners,
                'pending': pending_partners,
                'by_type': {
                    'development': development_partners,
                    'environmental': environmental_partners,
                    'corporate': corporate_partners,
                    'ngo': ngo_partners
                }
            }
        }, status=status.HTTP_200_OK)