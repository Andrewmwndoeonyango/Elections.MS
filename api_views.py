# =====================================================
# DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM API
# =====================================================

from rest_framework import serializers, status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Max, F, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.http import Http404

from voting.models import (
    County, Constituency, Ward, PollingStation, 
    Candidate, Position, Party, Result, AggregatedResult, Winner
)

# =====================================================
# SERIALIZERS
# =====================================================

class ResultSerializer(serializers.ModelSerializer):
    """Serializer for Result model with validation"""
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    polling_station_name = serializers.CharField(source='polling_station.name', read_only=True)
    party_name = serializers.CharField(source='candidate.party.name', read_only=True)
    position_name = serializers.CharField(source='candidate.position.name', read_only=True)
    
    class Meta:
        model = Result
        fields = [
            'id', 'polling_station', 'candidate', 'votes', 'voting_session',
            'candidate_name', 'polling_station_name', 'party_name', 'position_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation for result entry"""
        polling_station = data['polling_station']
        candidate = data['candidate']
        
        # Validate candidate belongs to correct area
        if candidate.position.name == 'MCA' and candidate.ward != polling_station.ward:
            raise serializers.ValidationError(
                "MCA candidate must belong to the same ward as polling station"
            )
        elif candidate.position.name == 'MP' and candidate.constituency != polling_station.constituency:
            raise serializers.ValidationError(
                "MP candidate must belong to the same constituency as polling station"
            )
        elif candidate.position.name in ['Governor', 'Senator', 'WOMEN_REP']:
            if candidate.county != polling_station.county:
                raise serializers.ValidationError(
                    f"{candidate.position.name} candidate must belong to the same county as polling station"
                )
        
        # Check for duplicate entries
        if Result.objects.filter(
            polling_station=polling_station,
            candidate=candidate,
            voting_session=data.get('voting_session')
        ).exists():
            raise serializers.ValidationError(
                "Result for this candidate at this polling station already exists"
            )
        
        return data

class AggregatedResultSerializer(serializers.ModelSerializer):
    """Serializer for aggregated results"""
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    party_name = serializers.CharField(source='candidate.party.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    
    class Meta:
        model = AggregatedResult
        fields = '__all__'

class WinnerSerializer(serializers.ModelSerializer):
    """Serializer for election winners"""
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    party_name = serializers.CharField(source='candidate.party.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    
    class Meta:
        model = Winner
        fields = '__all__'

# =====================================================
# PERMISSIONS
# =====================================================

class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission: Admin can edit, others can read"""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsResultManager(permissions.BasePermission):
    """Permission for result management"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Only admins can modify results
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_staff
        return True

# =====================================================
# API VIEWS
# =====================================================

class ResultViewSet(viewsets.ModelViewSet):
    """CRUD operations for election results"""
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsResultManager]
    filterset_fields = ['polling_station', 'candidate', 'voting_session']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'polling_station__name']
    ordering_fields = ['votes', 'created_at']
    ordering = ['-votes']
    
    def perform_create(self, serializer):
        """Set created_by when creating result"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Audit trail for result updates"""
        old_result = self.get_object()
        serializer.save(created_by=self.request.user)
        
        # Create backup entry
        ResultBackup.objects.create(
            result=self.get_object(),
            polling_station=old_result.polling_station,
            candidate=old_result.candidate,
            votes=old_result.votes,
            action_type='UPDATE',
            performed_by=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create results for efficiency"""
        results_data = request.data.get('results', [])
        
        if not results_data:
            return Response(
                {'error': 'No results data provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                created_results = []
                for result_data in results_data:
                    serializer = self.get_serializer(data=result_data)
                    serializer.is_valid(raise_exception=True)
                    result = serializer.save(created_by=request.user)
                    created_results.append(result)
                
                return Response(
                    ResultSerializer(created_results, many=True).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# =====================================================
# RESULTS AGGREGATION API
# =====================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_aggregated_results(request, area_type, area_id, position_name=None):
    """
    Get aggregated results for a specific area
    
    URL patterns:
    - /api/results/ward/{ward_id}/mca/
    - /api/results/constituency/{constituency_id}/mp/
    - /api/results/county/{county_id}/governor/
    - /api/results/county/{county_id}/senator/
    - /api/results/county/{county_id}/women_rep/
    """
    
    try:
        if area_type == 'ward' and position_name == 'MCA':
            results = Result.objects.get_mca_results_by_ward(area_id)
        elif area_type == 'constituency' and position_name == 'MP':
            results = Result.objects.get_mp_results_by_constituency(area_id)
        elif area_type == 'county' and position_name in ['Governor', 'Senator', 'WOMEN_REP']:
            results = Result.objects.get_county_results(area_id, position_name)
        else:
            return Response(
                {'error': 'Invalid area type and position combination'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add participation statistics
        stats = Result.objects.get_participation_stats(area_type, area_id)
        
        return Response({
            'results': list(results),
            'statistics': stats,
            'area_type': area_type,
            'area_id': area_id,
            'position': position_name
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_results_dashboard(request):
    """Get comprehensive results dashboard data"""
    
    # Get summary statistics
    total_results = Result.objects.count()
    total_votes = Result.objects.aggregate(total=Sum('votes'))['total'] or 0
    
    # Get recent results
    recent_results = Result.objects.order_by('-updated_at')[:10]
    
    # Get top performing candidates
    top_candidates = Result.objects.values(
        'candidate__id',
        'candidate__first_name',
        'candidate__last_name',
        'candidate__party__name',
        'candidate__position__name'
    ).annotate(
        total_votes=Sum('votes')
    ).order_by('-total_votes')[:10]
    
    return Response({
        'summary': {
            'total_results': total_results,
            'total_votes': total_votes,
            'total_candidates': Candidate.objects.count(),
            'total_polling_stations': PollingStation.objects.count()
        },
        'recent_results': ResultSerializer(recent_results, many=True).data,
        'top_candidates': list(top_candidates)
    })

# =====================================================
# WINNER DETERMINATION API
# =====================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_winners(request):
    """
    Get election winners
    
    Query parameters:
    - level: county, constituency, ward
    - id: area ID
    - position: specific position (optional)
    """
    
    level = request.GET.get('level')
    area_id = request.GET.get('id')
    position = request.GET.get('position')
    
    if not level or not area_id:
        return Response(
            {'error': 'Level and ID parameters are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if level == 'county':
            if position:
                # Get specific position winner
                winner = Result.objects.get_winner_for_area('county', area_id, position)
                return Response({'winner': winner} if winner else Response({'winner': None}))
            else:
                # Get all county winners
                winners = Winner.objects.get_winners_by_county(area_id)
                return Response({'winners': winners})
        
        elif level == 'constituency' and (not position or position == 'MP'):
            winner = Winner.objects.get_mp_winner_by_constituency(area_id)
            return Response({'winner': winner} if winner else Response({'winner': None}))
        
        elif level == 'ward' and (not position or position == 'MCA'):
            winner = Winner.objects.get_mca_winner_by_ward(area_id)
            return Response({'winner': winner} if winner else Response({'winner': None}))
        
        else:
            return Response(
                {'error': 'Invalid level and position combination'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_winners(request):
    """Get all winners across all areas"""
    
    # Get all county winners
    county_winners = []
    counties = County.objects.all()
    
    for county in counties:
        winners = Winner.objects.get_winners_by_county(county.id)
        for position, winner in winners.items():
            county_winners.append({
                'county': county.name,
                'position': position,
                'winner': winner
            })
    
    # Get all constituency winners
    constituency_winners = []
    constituencies = Constituency.objects.all()
    
    for constituency in constituencies:
        winner = Winner.objects.get_mp_winner_by_constituency(constituency.id)
        if winner:
            constituency_winners.append({
                'constituency': constituency.name,
                'county': constituency.county.name,
                'position': 'MP',
                'winner': winner
            })
    
    # Get all ward winners (limited for performance)
    ward_winners = []
    wards = Ward.objects.all()[:100]  # Limit to first 100 for demo
    
    for ward in wards:
        winner = Winner.objects.get_mca_winner_by_ward(ward.id)
        if winner:
            ward_winners.append({
                'ward': ward.name,
                'constituency': ward.constituency.name,
                'county': ward.constituency.county.name,
                'position': 'MCA',
                'winner': winner
            })
    
    return Response({
        'county_winners': county_winners,
        'constituency_winners': constituency_winners,
        'ward_winners': ward_winners,
        'summary': {
            'total_county_winners': len(county_winners),
            'total_constituency_winners': len(constituency_winners),
            'total_ward_winners': len(ward_winners)
        }
    })

# =====================================================
# EXPORT FUNCTIONALITY
# =====================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_results(request, format='csv'):
    """Export results in CSV or PDF format"""
    
    export_format = request.GET.get('format', 'csv')
    area_type = request.GET.get('area_type')
    area_id = request.GET.get('area_id')
    position = request.GET.get('position')
    
    if export_format not in ['csv', 'pdf']:
        return Response(
            {'error': 'Format must be csv or pdf'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if area_type and area_id and position:
            # Export specific area results
            if area_type == 'ward' and position == 'MCA':
                results = Result.objects.get_mca_results_by_ward(area_id)
            elif area_type == 'constituency' and position == 'MP':
                results = Result.objects.get_mp_results_by_constituency(area_id)
            elif area_type == 'county':
                results = Result.objects.get_county_results(area_id, position)
            else:
                return Response(
                    {'error': 'Invalid parameters'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Export all results
            results = Result.objects.values(
                'candidate__first_name',
                'candidate__last_name',
                'candidate__party__name',
                'candidate__position__name',
                'polling_station__name',
                'polling_station__ward__name',
                'polling_station__constituency__name',
                'polling_station__county__name',
                'votes'
            ).order_by('-votes')
        
        if export_format == 'csv':
            return generate_csv_export(results)
        else:
            return generate_pdf_export(results)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def generate_csv_export(results):
    """Generate CSV export"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="election_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Candidate Name', 'Party', 'Position', 'Polling Station',
        'Ward', 'Constitituency', 'County', 'Votes'
    ])
    
    for result in results:
        writer.writerow([
            result.get('candidate__first_name', '') + ' ' + result.get('candidate__last_name', ''),
            result.get('candidate__party__name', ''),
            result.get('candidate__position__name', ''),
            result.get('polling_station__name', ''),
            result.get('polling_station__ward__name', ''),
            result.get('polling_station__constituency__name', ''),
            result.get('polling_station__county__name', ''),
            result.get('votes', 0)
        ])
    
    return response

def generate_pdf_export(results):
    """Generate PDF export"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="election_results.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Create table data
    data = [['Candidate', 'Party', 'Position', 'Votes']]
    
    for result in results:
        candidate_name = f"{result.get('candidate__first_name', '')} {result.get('candidate__last_name', '')}"
        data.append([
            candidate_name,
            result.get('candidate__party__name', ''),
            result.get('candidate__position__name', ''),
            str(result.get('votes', 0))
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    # Build PDF
    elements = []
    elements.append(Paragraph("Election Results Report", styles['Title']))
    elements.append(table)
    
    doc.build(elements)
    return response

# =====================================================
# URL PATTERNS
# =====================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/results/ward/<int:ward_id>/mca/', get_aggregated_results, name='ward_mca_results'),
    path('api/results/constituency/<int:constituency_id>/mp/', get_aggregated_results, name='constituency_mp_results'),
    path('api/results/county/<int:county_id>/governor/', get_aggregated_results, name='county_governor_results'),
    path('api/results/county/<int:county_id>/senator/', get_aggregated_results, name='county_senator_results'),
    path('api/results/county/<int:county_id>/women_rep/', get_aggregated_results, name='county_women_rep_results'),
    path('api/results/dashboard/', get_results_dashboard, name='results_dashboard'),
    path('api/winners/', get_winners, name='get_winners'),
    path('api/winners/all/', get_all_winners, name='get_all_winners'),
    path('api/export/', export_results, name='export_results'),
]
