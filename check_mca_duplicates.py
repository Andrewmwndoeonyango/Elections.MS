#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Candidate, Position
from django.db.models import Count

def check_mca_duplicates():
    mca_position = Position.objects.get(name='MCA')
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    
    print(f'Total MCA candidates: {total_mcas}')
    
    # Check for duplicate candidates by name
    duplicates = Candidate.objects.filter(position=mca_position).values('first_name', 'last_name').annotate(count=Count('id')).filter(count__gt=1)
    
    print(f'Number of duplicate candidate names: {duplicates.count()}')
    for dup in duplicates[:10]:
        print(f'{dup["first_name"]} {dup["last_name"]}: {dup["count"]} entries')
    
    # Check for duplicate ID numbers
    duplicate_ids = Candidate.objects.filter(position=mca_position).values('id_number').annotate(count=Count('id')).filter(count__gt=1)
    print(f'Number of duplicate ID numbers: {duplicate_ids.count()}')
    for dup_id in duplicate_ids[:10]:
        print(f'{dup_id["id_number"]}: {dup_id["count"]} entries')
    
    # Show some sample candidates
    print('\nSample candidates:')
    for candidate in Candidate.objects.filter(position=mca_position)[:20]:
        print(f'{candidate.first_name} {candidate.last_name} - {candidate.id_number} - {candidate.ward.name if candidate.ward else "No ward"}')
    
    return total_mcas

if __name__ == '__main__':
    check_mca_duplicates()
