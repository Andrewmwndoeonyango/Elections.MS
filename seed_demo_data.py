#!/usr/bin/env python
"""
DISTINCTION-LEVEL ELECTION MANAGEMENT SYSTEM
DEMO DATA SEEDING SCRIPT
"""

import os
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import (
    County, Constituency, Ward, PollingStation, 
    Candidate, Position, Party, Result, VotingSession
)
from django.contrib.auth.models import User

def create_admin_user():
    """Create admin user for demo"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@elections.com', 'admin123')
        print("✅ Admin user created (username: admin, password: admin123)")
    else:
        print("ℹ️  Admin user already exists")

def create_voting_session():
    """Create a voting session for demo"""
    if not VotingSession.objects.filter(name='General Election 2027').exists():
        session = VotingSession.objects.create(
            name='General Election 2027',
            description='Kenya General Election Demonstration',
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True
        )
        print(f"✅ Voting session created: {session.name}")
    else:
        print("ℹ️  Voting session already exists")

def seed_sample_results():
    """Seed sample election results for demonstration"""
    
    print("\n🗳️  SEEDING SAMPLE ELECTION RESULTS...")
    
    # Get voting session
    session = VotingSession.objects.first()
    if not session:
        print("❌ No voting session found")
        return
    
    # Get all candidates
    candidates = Candidate.objects.all()
    polling_stations = PollingStation.objects.all()
    
    if not candidates.exists():
        print("❌ No candidates found. Please seed candidates first.")
        return
    
    if not polling_stations.exists():
        print("❌ No polling stations found. Please seed polling stations first.")
        return
    
    # Clear existing results
    Result.objects.all().delete()
    print("🗑️  Cleared existing results")
    
    results_created = 0
    
    # Create results for each candidate at relevant polling stations
    for candidate in candidates:
        # Determine relevant polling stations based on candidate position
        if candidate.position.name == 'MCA' and candidate.ward:
            stations = PollingStation.objects.filter(ward=candidate.ward)
        elif candidate.position.name == 'MP' and candidate.constituency:
            stations = PollingStation.objects.filter(constituency=candidate.constituency)
        elif candidate.position.name in ['Governor', 'Senator', 'WOMEN_REP'] and candidate.county:
            stations = PollingStation.objects.filter(county=candidate.county)
        else:
            continue
        
        # Create results at each relevant polling station
        for station in stations:
            # Generate realistic vote counts
            base_votes = random.randint(50, 500)
            
            # Add some variation based on candidate party popularity
            party_popularity = {
                'UDA': 1.3,
                'JUBILEE': 1.1,
                'ODM': 1.2,
                'WIPER': 1.0,
                'INDEPENDENT': 0.8,
                'KANU': 0.9,
                'DAP-K': 0.7,
                'PNU': 0.6
            }
            
            party_multiplier = party_popularity.get(candidate.party.name, 1.0)
            votes = int(base_votes * party_multiplier * random.uniform(0.8, 1.2))
            
            # Create result entry
            result = Result.objects.create(
                polling_station=station,
                candidate=candidate,
                votes=votes,
                voting_session=session
            )
            results_created += 1
    
    print(f"✅ Created {results_created} sample results")
    
    # Create some close races for demonstration
    create_close_races(session)
    
    # Calculate and display summary
    total_votes = Result.objects.aggregate(total=models.Sum('votes'))['total'] or 0
    total_results = Result.objects.count()
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   Total Results: {total_results}")
    print(f"   Total Votes: {total_votes:,}")
    print(f"   Average Votes per Result: {total_votes / total_results:.1f}")

def create_close_races(session):
    """Create some close races for demonstration"""
    
    print("\n🏁 CREATING CLOSE RACES...")
    
    # Find some wards with multiple MCA candidates
    wards_with_multiple_mcas = Ward.objects.annotate(
        mca_count=models.Count('ward_candidate', filter=models.Q(ward_candidate__position__name='MCA'))
    ).filter(mca_count__gte=3)[:5]
    
    for ward in wards_with_multiple_mcas:
        mca_candidates = Candidate.objects.filter(position__name='MCA', ward=ward)
        stations = PollingStation.objects.filter(ward=ward)
        
        if mca_candidates.count() >= 3 and stations.exists():
            # Create a close race
            base_votes = 200
            
            for i, candidate in enumerate(mca_candidates[:3]):
                # Make it close: 200, 195, 190 votes
                votes = base_votes - (i * 5)
                
                for station in stations:
                    Result.objects.update_or_create(
                        polling_station=station,
                        candidate=candidate,
                        voting_session=session,
                        defaults={'votes': votes}
                    )
    
    print("✅ Close races created for demonstration")

def create_demo_scenarios():
    """Create specific demo scenarios"""
    
    print("\n🎭 CREATING DEMO SCENARIOS...")
    
    # Scenario 1: Clear winner in Nairobi Governor race
    nairobi_county = County.objects.get(name='Nairobi')
    governor_candidates = Candidate.objects.filter(
        position__name='Governor', 
        county=nairobi_county
    )
    
    if governor_candidates.exists():
        # Make first candidate win clearly
        winner = governor_candidates.first()
        stations = PollingStation.objects.filter(county=nairobi_county)
        
        for station in stations:
            Result.objects.update_or_create(
                polling_station=station,
                candidate=winner,
                voting_session=VotingSession.objects.first(),
                defaults={'votes': random.randint(800, 1200)}
            )
        
        # Give other candidates fewer votes
        for candidate in governor_candidates[1:]:
            for station in stations:
                Result.objects.update_or_create(
                    polling_station=station,
                    candidate=candidate,
                    voting_session=VotingSession.objects.first(),
                    defaults={'votes': random.randint(200, 400)}
                )
    
    # Scenario 2: Tie situation (for demonstration of edge cases)
    # Find a small ward and create a tie
    small_ward = Ward.objects.annotate(
        station_count=models.Count('pollingstation')
    ).filter(station_count=1).first()
    
    if small_ward:
        mca_candidates = Candidate.objects.filter(position__name='MCA', ward=small_ward)[:2]
        station = PollingStation.objects.filter(ward=small_ward).first()
        
        if mca_candidates.count() == 2 and station:
            # Create exact tie
            for candidate in mca_candidates:
                Result.objects.update_or_create(
                    polling_station=station,
                    candidate=candidate,
                    voting_session=VotingSession.objects.first(),
                    defaults={'votes': 150}
                )
    
    print("✅ Demo scenarios created")

def generate_participation_statistics():
    """Generate and display participation statistics"""
    
    print("\n📈 PARTICIPATION STATISTICS:")
    
    # Overall statistics
    total_registered = PollingStation.objects.aggregate(
        total=models.Sum('registered_voters')
    )['total'] or 0
    
    total_votes_cast = Result.objects.aggregate(
        total=models.Sum('votes')
    )['total'] or 0
    
    overall_turnout = (total_votes_cast / total_registered * 100) if total_registered > 0 else 0
    
    print(f"   Registered Voters: {total_registered:,}")
    print(f"   Votes Cast: {total_votes_cast:,}")
    print(f"   Overall Turnout: {overall_turnout:.1f}%")
    
    # Top 5 counties by turnout
    county_turnouts = []
    for county in County.objects.all():
        registered = PollingStation.objects.filter(county=county).aggregate(
            total=models.Sum('registered_voters')
        )['total'] or 0
        
        votes = Result.objects.filter(polling_station__county=county).aggregate(
            total=models.Sum('votes')
        )['total'] or 0
        
        turnout = (votes / registered * 100) if registered > 0 else 0
        
        county_turnouts.append({
            'county': county.name,
            'turnout': turnout,
            'votes': votes,
            'registered': registered
        })
    
    county_turnouts.sort(key=lambda x: x['turnout'], reverse=True)
    
    print("\n   TOP 5 COUNTIES BY TURNOUT:")
    for i, county in enumerate(county_turnouts[:5]):
        print(f"   {i+1}. {county['county']}: {county['turnout']:.1f}%")

def display_demo_summary():
    """Display summary of demo data"""
    
    print("\n" + "="*60)
    print("🎉 DEMO DATA SETUP COMPLETE!")
    print("="*60)
    
    print(f"\n📊 SYSTEM SUMMARY:")
    print(f"   Counties: {County.objects.count()}")
    print(f"   Constituencies: {Constituency.objects.count()}")
    print(f"   Wards: {Ward.objects.count()}")
    print(f"   Polling Stations: {PollingStation.objects.count()}")
    print(f"   Candidates: {Candidate.objects.count()}")
    print(f"   Results Entered: {Result.objects.count()}")
    
    print(f"\n👤 ADMIN ACCESS:")
    print(f"   URL: http://localhost:8000/admin/")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    
    print(f"\n🌐 DASHBOARD ACCESS:")
    print(f"   URL: http://localhost:8000/dashboard/")
    print(f"   Results Dashboard: http://localhost:8000/results/dashboard/")
    
    print(f"\n🔧 API ENDPOINTS:")
    print(f"   Results API: http://localhost:8000/api/results/")
    print(f"   Winners API: http://localhost:8000/api/winners/")
    print(f"   Export API: http://localhost:8000/api/export/")
    
    print(f"\n📋 DEMO SCENARIOS INCLUDED:")
    print(f"   ✅ Clear winner in Nairobi Governor race")
    print(f"   ✅ Close races in multiple wards")
    print(f"   ✅ Tie situation for edge case testing")
    print(f"   ✅ Realistic voter turnout patterns")
    print(f"   ✅ Party performance variations")
    
    print(f"\n🎯 KEY FEATURES TO DEMONSTRATE:")
    print(f"   1. Results aggregation (ward → constituency → county)")
    print(f"   2. Winner determination algorithm")
    print(f"   3. Real-time dashboard with charts")
    print(f"   4. Export functionality (CSV/PDF)")
    print(f"   5. Role-based access control")
    print(f"   6. Data validation and integrity")
    print(f"   7. Performance with large datasets")
    
    print("\n" + "="*60)

def main():
    """Main seeding function"""
    
    print("🚀 STARTING DEMO DATA SEEDING...")
    print("="*60)
    
    try:
        # Create admin user
        create_admin_user()
        
        # Create voting session
        create_voting_session()
        
        # Seed sample results
        seed_sample_results()
        
        # Create demo scenarios
        create_demo_scenarios()
        
        # Generate statistics
        generate_participation_statistics()
        
        # Display summary
        display_demo_summary()
        
    except Exception as e:
        print(f"\n❌ ERROR DURING SEEDING: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
