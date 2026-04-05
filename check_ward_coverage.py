#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Candidate, Position, Ward, County

def check_ward_coverage():
    mca_position = Position.objects.get(name='MCA')
    
    # Get total wards and counties
    total_wards = Ward.objects.count()
    total_counties = County.objects.count()
    
    # Get wards with MCA candidates
    wards_with_mcas = Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward').distinct().count()
    
    # Get MCA candidates count
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    
    print(f'=== WARD AND CANDIDATE ANALYSIS ===')
    print(f'Total counties: {total_counties}')
    print(f'Total wards: {total_wards}')
    print(f'Wards with MCA candidates: {wards_with_mcas}')
    print(f'Wards without MCA candidates: {total_wards - wards_with_mcas}')
    print(f'Total MCA candidates: {total_mcas}')
    
    # Average candidates per ward
    if wards_with_mcas > 0:
        avg_candidates_per_ward = total_mcas / wards_with_mcas
        print(f'Average candidates per ward: {avg_candidates_per_ward:.2f}')
    
    # Check by county
    print(f'\n=== BY COUNTY ===')
    counties = County.objects.all()
    for county in counties[:10]:  # Show first 10 counties
        county_wards = Ward.objects.filter(constituency__county=county).count()
        county_mcas = Candidate.objects.filter(position=mca_position, county=county).count()
        print(f'{county.name}: {county_wards} wards, {county_mcas} candidates')
    
    # Expected calculation
    print(f'\n=== EXPECTED VS ACTUAL ===')
    print(f'If each ward had 1 candidate: {total_wards} candidates')
    print(f'If each ward had 2 candidates: {total_wards * 2} candidates')
    print(f'Actual candidates: {total_mcas}')
    
    # Check for candidates without wards
    candidates_without_wards = Candidate.objects.filter(position=mca_position, ward__isnull=True).count()
    print(f'Candidates without wards: {candidates_without_wards}')
    
    return total_wards, wards_with_mcas, total_mcas

if __name__ == '__main__':
    check_ward_coverage()
