# =====================================================
# DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM VIEWS
# =====================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from voting.models import (
    County, Constituency, Ward, PollingStation, 
    Candidate, Position, Party, Result, Winner
)
from .forms import LoginForm, ResultForm, CandidateForm

# =====================================================
# AUTHENTICATION VIEWS
# =====================================================

def login_view(request):
    """Custom login view with role-based redirect"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Role-based redirect
                if user.is_staff:
                    return redirect('dashboard')
                else:
                    return redirect('results')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

# =====================================================
# DASHBOARD VIEWS
# =====================================================

@login_required
def dashboard_view(request):
    """Main dashboard with overview statistics"""
    
    # Get summary statistics
    total_counties = County.objects.count()
    total_constituencies = Constituency.objects.count()
    total_wards = Ward.objects.count()
    total_polling_stations = PollingStation.objects.count()
    
    # Get candidate counts by position
    candidate_stats = Candidate.objects.values('position__name').annotate(count=Count('id'))
    
    # Get recent results
    recent_results = Result.objects.select_related(
        'candidate', 'polling_station', 'candidate__party'
    ).order_by('-updated_at')[:10]
    
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
    
    # Get participation statistics
    total_votes = Result.objects.aggregate(total=Sum('votes'))['total'] or 0
    total_registered_voters = PollingStation.objects.aggregate(
        total=Sum('registered_voters')
    )['total'] or 0
    
    turnout_percentage = (total_votes / total_registered_voters * 100) if total_registered_voters > 0 else 0
    
    context = {
        'total_counties': total_counties,
        'total_constituencies': total_constituencies,
        'total_wards': total_wards,
        'total_polling_stations': total_polling_stations,
        'candidate_stats': candidate_stats,
        'recent_results': recent_results,
        'top_candidates': top_candidates,
        'total_votes': total_votes,
        'total_registered_voters': total_registered_voters,
        'turnout_percentage': turnout_percentage,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def results_view(request):
    """Results viewing page with filtering"""
    
    # Get filter parameters
    county_id = request.GET.get('county')
    constituency_id = request.GET.get('constituency')
    ward_id = request.GET.get('ward')
    position = request.GET.get('position', 'MCA')
    
    # Build base query
    results_query = Result.objects.select_related(
        'candidate', 'polling_station', 'candidate__party', 'candidate__position'
    )
    
    # Apply filters
    if ward_id and position == 'MCA':
        results_query = results_query.filter(
            polling_station__ward_id=ward_id,
            candidate__position__name='MCA'
        )
    elif constituency_id and position == 'MP':
        results_query = results_query.filter(
            polling_station__constituency_id=constituency_id,
            candidate__position__name='MP'
        )
    elif county_id and position in ['Governor', 'Senator', 'WOMEN_REP']:
        results_query = results_query.filter(
            polling_station__county_id=county_id,
            candidate__position__name=position
        )
    
    # Get aggregated results
    if ward_id and position == 'MCA':
        results = results_query.values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    elif constituency_id and position == 'MP':
        results = results_query.values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    elif county_id and position in ['Governor', 'Senator', 'WOMEN_REP']:
        results = results_query.values(
            'candidate__id',
            'candidate__first_name',
            'candidate__last_name',
            'candidate__party__name'
        ).annotate(
            total_votes=Sum('votes')
        ).order_by('-total_votes')
    else:
        results = []
    
    # Calculate percentages
    total_votes = sum(r['total_votes'] for r in results)
    for result in results:
        result['percentage'] = (result['total_votes'] / total_votes * 100) if total_votes > 0 else 0
    
    # Get filter options
    counties = County.objects.all()
    constituencies = []
    wards = []
    
    if county_id:
        constituencies = Constituency.objects.filter(county_id=county_id)
        if constituency_id:
            wards = Ward.objects.filter(constituency_id=constituency_id)
    
    context = {
        'results': results,
        'counties': counties,
        'constituencies': constituencies,
        'wards': wards,
        'selected_county': county_id,
        'selected_constituency': constituency_id,
        'selected_ward': ward_id,
        'selected_position': position,
        'total_votes': total_votes,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'results.html', context)

# =====================================================
# DATA MANAGEMENT VIEWS (ADMIN ONLY)
# =====================================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def candidates_view(request):
    """Manage candidates"""
    
    candidates = Candidate.objects.select_related(
        'position', 'party', 'county', 'constituency', 'ward'
    ).order_by('position__name', 'county__name', 'first_name')
    
    # Filter by position
    position_filter = request.GET.get('position')
    if position_filter:
        candidates = candidates.filter(position__name=position_filter)
    
    # Pagination
    paginator = Paginator(candidates, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    positions = Position.objects.all()
    
    context = {
        'page_obj': page_obj,
        'positions': positions,
        'selected_position': position_filter,
    }
    
    return render(request, 'candidates.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def counties_view(request):
    """Manage counties and their data"""
    
    counties = County.objects.annotate(
        constituency_count=Count('constituency'),
        ward_count=Count('constituency__ward'),
        polling_station_count=Count('constituency__ward__pollingstation')
    ).order_by('name')
    
    context = {
        'counties': counties,
    }
    
    return render(request, 'counties.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def constituencies_view(request):
    """Manage constituencies"""
    
    county_filter = request.GET.get('county')
    
    constituencies = Constituency.objects.select_related('county').annotate(
        ward_count=Count('ward'),
        polling_station_count=Count('ward__pollingstation')
    ).order_by('county__name', 'name')
    
    if county_filter:
        constituencies = constituencies.filter(county_id=county_filter)
    
    counties = County.objects.all()
    
    context = {
        'constituencies': constituencies,
        'counties': counties,
        'selected_county': county_filter,
    }
    
    return render(request, 'constituencies.html', context)

# =====================================================
# RESULT MANAGEMENT VIEWS (ADMIN ONLY)
# =====================================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_results_view(request):
    """Manage election results"""
    
    # Get filter parameters
    county_id = request.GET.get('county')
    constituency_id = request.GET.get('constituency')
    ward_id = request.GET.get('ward')
    polling_station_id = request.GET.get('polling_station')
    
    # Build query
    results = Result.objects.select_related(
        'candidate', 'polling_station', 'candidate__party', 'created_by'
    ).order_by('-updated_at')
    
    # Apply filters
    if county_id:
        results = results.filter(polling_station__county_id=county_id)
    if constituency_id:
        results = results.filter(polling_station__constituency_id=constituency_id)
    if ward_id:
        results = results.filter(polling_station__ward_id=ward_id)
    if polling_station_id:
        results = results.filter(polling_station_id=polling_station_id)
    
    # Pagination
    paginator = Paginator(results, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    counties = County.objects.all()
    constituencies = []
    wards = []
    polling_stations = []
    
    if county_id:
        constituencies = Constituency.objects.filter(county_id=county_id)
        if constituency_id:
            wards = Ward.objects.filter(constituency_id=constituency_id)
            if ward_id:
                polling_stations = PollingStation.objects.filter(ward_id=ward_id)
    
    context = {
        'page_obj': page_obj,
        'counties': counties,
        'constituencies': constituencies,
        'wards': wards,
        'polling_stations': polling_stations,
        'selected_county': county_id,
        'selected_constituency': constituency_id,
        'selected_ward': ward_id,
        'selected_polling_station': polling_station_id,
    }
    
    return render(request, 'manage_results.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_result_view(request):
    """Add new election result"""
    
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.created_by = request.user
            result.save()
            
            messages.success(request, 'Result added successfully!')
            return redirect('manage_results')
    else:
        form = ResultForm()
    
    return render(request, 'add_result.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_result_view(request, result_id):
    """Edit existing election result"""
    
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Result updated successfully!')
            return redirect('manage_results')
    else:
        form = ResultForm(instance=result)
    
    return render(request, 'edit_result.html', {'form': form, 'result': result})

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_http_methods(['POST'])
def delete_result_view(request, result_id):
    """Delete election result"""
    
    result = get_object_or_404(Result, id=result_id)
    result.delete()
    
    messages.success(request, 'Result deleted successfully!')
    return redirect('manage_results')

# =====================================================
# AJAX API VIEWS FOR FRONTEND
# =====================================================

@login_required
def api_counties(request):
    """API endpoint for counties"""
    counties = County.objects.all().values('id', 'name')
    return JsonResponse(list(counties), safe=False)

@login_required
def api_constituencies(request):
    """API endpoint for constituencies"""
    county_id = request.GET.get('county_id')
    
    if county_id:
        constituencies = Constituency.objects.filter(
            county_id=county_id
        ).values('id', 'name')
    else:
        constituencies = Constituency.objects.all().values('id', 'name')
    
    return JsonResponse(list(constituencies), safe=False)

@login_required
def api_wards(request):
    """API endpoint for wards"""
    constituency_id = request.GET.get('constituency_id')
    
    if constituency_id:
        wards = Ward.objects.filter(
            constituency_id=constituency_id
        ).values('id', 'name')
    else:
        wards = Ward.objects.all().values('id', 'name')
    
    return JsonResponse(list(wards), safe=False)

@login_required
def api_polling_stations(request):
    """API endpoint for polling stations"""
    ward_id = request.GET.get('ward_id')
    
    if ward_id:
        stations = PollingStation.objects.filter(
            ward_id=ward_id
        ).values('id', 'name', 'registered_voters')
    else:
        stations = PollingStation.objects.all().values('id', 'name', 'registered_voters')
    
    return JsonResponse(list(stations), safe=False)

@login_required
def api_candidates(request):
    """API endpoint for candidates"""
    position = request.GET.get('position')
    county_id = request.GET.get('county_id')
    constituency_id = request.GET.get('constituency_id')
    ward_id = request.GET.get('ward_id')
    
    candidates = Candidate.objects.select_related('party')
    
    if position:
        candidates = candidates.filter(position__name=position)
    if county_id:
        candidates = candidates.filter(county_id=county_id)
    if constituency_id:
        candidates = candidates.filter(constituency_id=constituency_id)
    if ward_id:
        candidates = candidates.filter(ward_id=ward_id)
    
    candidates_data = candidates.values(
        'id', 'first_name', 'last_name', 'party__name', 'party__id'
    )
    
    return JsonResponse(list(candidates_data), safe=False)

# =====================================================
# ERROR HANDLERS
# =====================================================

def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    """Custom 500 error page"""
    return render(request, 'errors/500.html', status=500)

# =====================================================
# UTILITY VIEWS
# =====================================================

@login_required
def export_results_view(request):
    """Export results in various formats"""
    
    format_type = request.GET.get('format', 'csv')
    area_type = request.GET.get('area_type')
    area_id = request.GET.get('area_id')
    position = request.GET.get('position')
    
    # This would integrate with the export_results API view
    # For now, redirect to API endpoint
    url = f'/api/export/?format={format_type}'
    if area_type and area_id:
        url += f'&area_type={area_type}&area_id={area_id}'
    if position:
        url += f'&position={position}'
    
    return redirect(url)

@login_required
def system_status_view(request):
    """System status and health check"""
    
    if not request.user.is_staff:
        return redirect('dashboard')
    
    # Get system statistics
    stats = {
        'counties': County.objects.count(),
        'constituencies': Constituency.objects.count(),
        'wards': Ward.objects.count(),
        'polling_stations': PollingStation.objects.count(),
        'candidates': Candidate.objects.count(),
        'results': Result.objects.count(),
        'total_votes': Result.objects.aggregate(total=Sum('votes'))['total'] or 0,
    }
    
    # Check for data integrity issues
    issues = []
    
    # Check for candidates without proper area assignments
    orphaned_candidates = Candidate.objects.filter(
        Q(county__isnull=True) | Q(constituency__isnull=True) | Q(ward__isnull=True)
    ).count()
    
    if orphaned_candidates > 0:
        issues.append(f'{orphaned_candidates} candidates with missing area assignments')
    
    # Check for results without proper candidates
    orphaned_results = Result.objects.filter(candidate__isnull=True).count()
    if orphaned_results > 0:
        issues.append(f'{orphaned_results} results with missing candidates')
    
    context = {
        'stats': stats,
        'issues': issues,
        'system_healthy': len(issues) == 0,
    }
    
    return render(request, 'system_status.html', context)
