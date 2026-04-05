#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Candidate, Position, Ward
from django.db.models import Count

def analyze_mca_duplicates():
    mca_position = Position.objects.get(name='MCA')
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    
    print(f'Total MCA candidates: {total_mcas}')
    
    # Get all duplicate names
    duplicates = Candidate.objects.filter(position=mca_position).values('first_name', 'last_name').annotate(count=Count('id')).filter(count__gt=1).order_by('-count')
    
    print(f'\nTop 20 most duplicated candidate names:')
    for i, dup in enumerate(duplicates[:20]):
        print(f'{i+1}. {dup["first_name"]} {dup["last_name"]}: {dup["count"]} entries')
    
    # Analyze one specific duplicate case
    print(f'\nAnalyzing "Agnes Kinya" (appears 132 times):')
    agnes_candidates = Candidate.objects.filter(position=mca_position, first_name='Agnes', last_name='Kinya')
    for i, candidate in enumerate(agnes_candidates[:10]):
        print(f'{i+1}. ID: {candidate.id_number}, Ward: {candidate.ward.name if candidate.ward else "None"}, Party: {candidate.party.name}')
    
    # Count unique wards
    unique_wards = Ward.objects.count()
    wards_with_candidates = Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward').distinct().count()
    
    print(f'\nWard analysis:')
    print(f'Total wards in database: {unique_wards}')
    print(f'Wards with MCA candidates: {wards_with_candidates}')
    
    # Expected vs actual
    print(f'\nExpected vs Actual:')
    print(f'Expected MCA candidates (approx): 2,900')
    print(f'Actual MCA candidates: {total_mcas}')
    print(f'Difference: {total_mcas - 2900}')
    
    return total_mcas

if __name__ == '__main__':
    analyze_mca_duplicates()
