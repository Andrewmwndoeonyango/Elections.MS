from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db import IntegrityError
from .models import (
    County, Constituency, Ward, PollingCenter, PollingStation,
    Position, Candidate, Voter, Vote, Party, OTPVerification
)
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie


def is_admin_user(user):
    return user.is_staff


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('voting:admin_dashboard')
        if hasattr(request.user, 'voter'):
            return redirect('voting:profile')
        return redirect('voting:register')

    context = {
        'counties': County.objects.count(),
        'constituencies': Constituency.objects.count(),
        'wards': Ward.objects.count(),
        'polling_centers': PollingCenter.objects.count(),
        'polling_stations': PollingStation.objects.count(),
        'total_entities': County.objects.count() + Constituency.objects.count() + Ward.objects.count() + PollingCenter.objects.count() + PollingStation.objects.count() + Candidate.objects.count(),
    }
    return render(request, 'voting/simple_home.html', context)


def public_dashboard(request):
    total_votes = 0
    try:
        total_votes = Vote.objects.count()
    except Exception:
        total_votes = 0

    context = {
        'total_counties': County.objects.count(),
        'total_constituencies': Constituency.objects.count(),
        'total_wards': Ward.objects.count(),
        'total_polling_stations': PollingStation.objects.count(),
        'total_candidates': Candidate.objects.count(),
        'total_votes': total_votes,
    }
    return render(request, 'dashboard.html', context)


def voter_portal(request):
    context = {
        'counties_count': County.objects.count(),
        'constituencies_count': Constituency.objects.count(),
        'wards_count': Ward.objects.count(),
        'candidates_count': Candidate.objects.count(),
        'registered_voters_count': Voter.objects.count(),
        'polling_stations_count': PollingStation.objects.count(),
    }
    return render(request, 'voter_portal.html', context)


def voter_education(request):
    return render(request, 'voting/voter_education.html')


@user_passes_test(is_admin_user, login_url='voting:login')
def admin_portal(request):
    context = {
        'counties_count': County.objects.count(),
        'constituencies_count': Constituency.objects.count(),
        'wards_count': Ward.objects.count(),
        'candidates_count': Candidate.objects.count(),
        'results_entered_count': Vote.objects.values('voter').distinct().count(),
        'total_votes_count': Vote.objects.count(),
    }
    return render(request, 'admin_portal.html', context)


@never_cache
@ensure_csrf_cookie
def register(request):
    # If user is already logged in and has voter profile, redirect to dashboard
    if request.user.is_authenticated and hasattr(request.user, 'voter'):
        return redirect('voting:dashboard')

    # If user is logged in but no voter profile, show message
    if request.user.is_authenticated:
        messages.info(
            request, f'Welcome {request.user.username}! Please complete your voter registration to access the dashboard.')

    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_number = request.POST.get('id_number')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        county_id = request.POST.get('county')
        constituency_id = request.POST.get('constituency')
        ward_id = request.POST.get('ward')
        polling_center_id = request.POST.get('polling_center')
        polling_station_id = request.POST.get('polling_station')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Handle user creation or update
        try:
            if request.user.is_authenticated:
                # Update existing user
                user = request.user
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
            else:
                # Create new user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

            # Handle polling station (dropdown selection only)
            polling_station_obj = None
            if polling_station_id:
                try:
                    polling_station_obj = PollingStation.objects.get(
                        id=polling_station_id)
                except PollingStation.DoesNotExist:
                    # Create a default polling station if the selected one doesn't exist
                    polling_center_obj = PollingCenter.objects.get(
                        id=polling_center_id)
                    polling_station_obj = PollingStation.objects.create(
                        name="Default Station",
                        center=polling_center_obj,
                        code=f"PS{PollingStation.objects.count() + 1:04d}"
                    )
            else:
                # Create a default polling station if none selected
                polling_center_obj = PollingCenter.objects.first()
                if not polling_center_obj:
                    polling_center_obj = PollingCenter.objects.create(
                        name="Default Center",
                        code="PC0001",
                        ward_id=1
                    )
                polling_station_obj = PollingStation.objects.create(
                    name="Default Station",
                    center=polling_center_obj,
                    code=f"PS{PollingStation.objects.count() + 1:04d}"
                )

            # Create voter profile
            voter = Voter.objects.create(
                user=user,
                id_number=id_number,
                phone_number=phone_number,
                county_id=county_id,
                constituency_id=constituency_id,
                ward_id=ward_id,
                polling_center_id=polling_center_id,
                polling_station=polling_station_obj,
            )

            # Generate and send OTP
            otp = OTPVerification.generate_otp(user)

            # Store user ID in session for OTP verification
            request.session['pending_user_id'] = user.id
            request.session['otp_sent'] = True

            messages.info(
                request, f'Registration successful! Your verification code is: {otp.otp_code}. Please enter this code to complete verification.')
            return redirect('voting:verify_otp')

        except IntegrityError as e:
            if 'username' in str(e):
                messages.error(
                    request, 'Username already exists. Please choose a different username.')
            elif 'id_number' in str(e):
                messages.error(
                    request, 'ID number already registered. This ID number has been used for another voter.')
            else:
                messages.error(
                    request, 'Registration failed. Please check your information and try again.')
            return redirect('voting:register')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('voting:register')

    counties = County.objects.all()
    return render(request, 'voting/register.html', {'counties': counties})


@never_cache
@ensure_csrf_cookie
def verify_otp(request):
    if not request.session.get('otp_sent') or not request.session.get('pending_user_id'):
        return redirect('voting:register')

    # Get the latest OTP for display
    user_id = request.session.get('pending_user_id')
    latest_otp = None
    try:
        user = User.objects.get(id=user_id)
        latest_otp = OTPVerification.objects.filter(
            user=user, is_used=False).order_by('-created_at').first()
    except User.DoesNotExist:
        pass

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')

        try:
            user = User.objects.get(id=user_id)
            otp = OTPVerification.objects.filter(
                user=user, otp_code=otp_code).first()

            if otp and otp.is_valid():
                # Mark OTP as used
                otp.is_used = True
                otp.save()

                # Mark voter as verified
                if hasattr(user, 'voter'):
                    user.voter.is_verified = True
                    user.voter.save()

                # Clear session
                del request.session['otp_sent']
                del request.session['pending_user_id']

                # Auto-login user
                login(request, user)

                messages.success(
                    request, 'Verification successful! Your account is now active.')
                return redirect('voting:dashboard')
            else:
                messages.error(
                    request, 'Invalid or expired verification code. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid session. Please register again.')
            return redirect('voting:register')

    context = {
        'otp_code': latest_otp.otp_code if latest_otp else None
    }
    return render(request, 'voting/verify_otp.html', context)


@never_cache
@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is a voter and is verified
            if hasattr(user, 'voter') and not user.voter.is_verified:
                messages.error(
                    request, 'Your account is not verified. Please complete OTP verification.')
                return redirect('voting:register')

            login(request, user)
            if user.is_staff:
                return redirect('voting:admin_dashboard')
            return redirect('voting:dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'voting/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('voting:home')


def dashboard(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to access your voter dashboard.')
        return redirect('voting:login')

    # If user is staff, redirect to admin dashboard instead
    if request.user.is_staff:
        return redirect('voting:admin_dashboard')

    if not hasattr(request.user, 'voter'):
        messages.info(
            request, 'Please complete voter registration to access the dashboard.')
        return redirect('voting:register')

    if not request.user.voter.is_verified:
        messages.error(
            request, 'Your voter account is not verified. Complete OTP verification first.')
        return redirect('voting:verify_otp')

    voter = request.user.voter
    positions = Position.objects.all()
    votes = Vote.objects.filter(voter=voter)
    voted_positions = [vote.position for vote in votes]

    context = {
        'voter': voter,
        'positions': positions,
        'voted_positions': voted_positions
    }
    return render(request, 'voting/dashboard.html', context)


@login_required
def profile(request):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')

    voter = request.user.voter
    return render(request, 'voting/profile.html', {'voter': voter})


@login_required
def vote(request, position):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')

    voter = request.user.voter
    position_obj = get_object_or_404(Position, name__iexact=position.upper())

    # Check if already voted for this position
    if Vote.objects.filter(voter=voter, position=position_obj).exists():
        messages.error(
            request, f'You have already voted for {position_obj.get_name_display()}')
        return redirect('voting:dashboard')

    # Get candidates based on position and voter's location
    candidates = Candidate.objects.filter(position=position_obj)
    position_name = position_obj.name

    if position_name == 'PRESIDENT':
        pass  # All voters can vote for president
    elif position_name in ['GOVERNOR', 'SENATOR', 'WOMEN_REP']:
        candidates = candidates.filter(county=voter.county)
    elif position_name == 'MP':
        candidates = candidates.filter(constituency=voter.constituency)
    else:  # MCA
        candidates = candidates.filter(ward=voter.ward)

    # Get vote statistics for each candidate
    candidate_stats = []
    total_votes = Vote.objects.filter(position=position_obj).count()

    for candidate in candidates:
        vote_count = Vote.objects.filter(candidate=candidate).count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0

        candidate_stats.append({
            'candidate': candidate,
            'vote_count': vote_count,
            'percentage': round(percentage, 1)
        })

    # Sort by vote count (highest first)
    candidate_stats.sort(key=lambda x: x['vote_count'], reverse=True)

    context = {
        'position': position_obj,
        'candidates': candidates,
        'candidate_stats': candidate_stats,
        'total_votes': total_votes
    }
    return render(request, 'voting/vote.html', context)


@login_required
@never_cache
@ensure_csrf_cookie
def confirm_vote(request, candidate_id, position):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:register')

    voter = request.user.voter
    if not voter.is_verified:
        messages.error(
            request, 'Your voter account is not verified. Complete OTP verification first.')
        return redirect('voting:verify_otp')

    position_obj = get_object_or_404(Position, name__iexact=position.upper())
    candidate = get_object_or_404(
        Candidate,
        id=candidate_id,
        position=position_obj
    )

    if request.method == 'POST':
        # Final check if already voted
        if Vote.objects.filter(voter=voter, position=position_obj).exists():
            messages.error(
                request, f'You have already voted for {position_obj.get_name_display()}')
            return redirect('voting:dashboard')

        # Create vote
        Vote.objects.create(
            voter=voter,
            position=position_obj,
            candidate=candidate
        )

        messages.success(
            request, f'Your vote for {position_obj.get_name_display()} has been recorded')
        return redirect('voting:vote_success')

    return render(request, 'voting/confirm_vote.html', {'candidate': candidate})


@login_required
def vote_success(request):
    return render(request, 'voting/vote_success.html')


@login_required
def voter_statistics(request):
    if not hasattr(request.user, 'voter'):
        messages.error(request, 'You are not registered as a voter')
        return redirect('voting:home')

    voter = request.user.voter

    # Get overall statistics
    total_voters = Voter.objects.filter(is_verified=True).count()
    total_votes = Vote.objects.count()

    # Get position-wise statistics
    positions = Position.objects.all()
    position_stats = []

    for position in positions:
        votes_for_position = Vote.objects.filter(position=position).count()
        candidates_for_position = Candidate.objects.filter(
            position=position).count()

        # Get candidates for this position
        top_candidates = []
        candidates = Candidate.objects.filter(position=position).select_related(
            'party', 'county', 'constituency', 'ward'
        )

        for candidate in candidates:
            vote_count = Vote.objects.filter(candidate=candidate).count()
            percentage = (vote_count / votes_for_position *
                          100) if votes_for_position > 0 else 0
            top_candidates.append({
                'candidate': candidate,
                'vote_count': vote_count,
                'percentage': round(percentage, 1)
            })

        # Sort by vote count
        top_candidates.sort(key=lambda x: x['vote_count'], reverse=True)

        position_stats.append({
            'position': position,
            'total_votes': votes_for_position,
            'candidates_count': candidates_for_position,
            'top_candidates': top_candidates
        })

    # Get voter's voting history
    voter_votes = Vote.objects.filter(
        voter=voter).select_related('candidate', 'position')

    context = {
        'total_voters': total_voters,
        'total_votes': total_votes,
        'position_stats': position_stats,
        'voter_votes': voter_votes,
        'voter': voter,
        'overall_turnout': round((total_votes / total_voters * 100), 1) if total_voters > 0 else 0
    }

    return render(request, 'voting/voter_statistics.html', context)


# Ajax views for dependent dropdowns


def load_constituencies(request):
    county_id = request.GET.get('county')
    if county_id:
        constituencies = Constituency.objects.filter(
            county_id=county_id).values('id', 'name').order_by('name')
        return JsonResponse(list(constituencies), safe=False)
    return JsonResponse([], safe=False)


def load_wards(request):
    constituency_id = request.GET.get('constituency')
    if constituency_id:
        wards = Ward.objects.filter(constituency_id=constituency_id).values(
            'id', 'name').order_by('name')
        return JsonResponse(list(wards), safe=False)
    return JsonResponse([], safe=False)


def load_polling_centers(request):
    ward_id = request.GET.get('ward')
    if ward_id:
        centers = PollingCenter.objects.filter(
            ward_id=ward_id).values('id', 'name').order_by('name')
        return JsonResponse(list(centers), safe=False)
    return JsonResponse([], safe=False)


def load_polling_stations(request):
    center_id = request.GET.get('polling_center')
    if center_id:
        try:
            stations = PollingStation.objects.filter(
                center_id=center_id).values('id', 'name').order_by('name')
            return JsonResponse(list(stations), safe=False)
        except Exception as e:
            print(f"Error loading polling stations: {e}")
            stations = [
                {'id': 1, 'name': 'Station 1'},
                {'id': 2, 'name': 'Station 2'},
                {'id': 3, 'name': 'Station 3'}
            ]
            return JsonResponse(stations, safe=False)

    return JsonResponse([], safe=False)


# Admin views


@user_passes_test(is_admin_user, login_url='voting:login')
@never_cache
def admin_dashboard(request):
    total_voters = Voter.objects.count()
    total_votes = Vote.objects.count()
    total_candidates = Candidate.objects.count()

    # Votes by position
    position_stats = Position.objects.annotate(
        total_votes=Count('vote', distinct=True),
        total_candidates=Count('candidate', distinct=True)
    )

    # Recent votes
    recent_votes = Vote.objects.select_related(
        'voter__user', 'position', 'candidate'
    ).order_by('-timestamp')[:10]

    # Registration trend
    registration_trend = Voter.objects.annotate(
        date=TruncDate('registration_date')
    ).values('date').annotate(count=Count('id')).order_by('date')[:30]

    context = {
        'total_voters': total_voters,
        'total_votes': total_votes,
        'total_candidates': total_candidates,
        'position_stats': position_stats,
        'recent_votes': recent_votes,
        'registration_trend': registration_trend
    }
    return render(request, 'voting/admin_dashboard.html', context)


@user_passes_test(is_admin_user, login_url='voting:login')
def election_statistics(request):
    positions = Position.objects.all()
    stats = []

    for position in positions:
        position_stats = {
            'position': position,
            'total_votes': Vote.objects.filter(position=position).count(),
            'candidates': []
        }

        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:
            votes = Vote.objects.filter(
                position=position, candidate=candidate).count()
            position_stats['candidates'].append({
                'candidate': candidate,
                'votes': votes,
                'percentage': (votes / position_stats['total_votes'] * 100) if position_stats['total_votes'] > 0 else 0
            })

        # Sort candidates by votes
        position_stats['candidates'].sort(
            key=lambda x: x['votes'], reverse=True)
        stats.append(position_stats)

    context = {
        'stats': stats,
        'last_updated': timezone.now()
    }
    return render(request, 'voting/election_statistics.html', context)
