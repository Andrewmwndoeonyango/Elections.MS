#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Candidate, Position, Ward, County, Party
from django.db.models import Count

def fix_mca_candidates():
    mca_position = Position.objects.get(name='MCA')
    
    print("=== CURRENT SITUATION ===")
    total_wards = Ward.objects.count()
    wards_with_mcas = Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward').distinct().count()
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    
    print(f"Total wards: {total_wards}")
    print(f"Wards with MCA candidates: {wards_with_mcas}")
    print(f"Total MCA candidates: {total_mcas}")
    
    print("\n=== STEP 1: DELETE ALL EXISTING MCA CANDIDATES ===")
    # Delete all existing MCA candidates to start fresh
    deleted_count = Candidate.objects.filter(position=mca_position).delete()[0]
    print(f"Deleted {deleted_count} existing MCA candidates")
    
    print("\n=== STEP 2: SELECT 1,450 WARDS ===")
    # Get exactly 1,450 wards (we'll take the first 1,450)
    target_wards = Ward.objects.all()[:1450]
    print(f"Selected {target_wards.count()} wards for candidate assignment")
    
    print("\n=== STEP 3: CREATE 2 CANDIDATES PER WARD ===")
    
    # Common candidate names to use
    first_names = ['John', 'Mary', 'Peter', 'Grace', 'David', 'Esther', 'Paul', 'Ruth', 'Anthony', 'Lucy', 
                   'Michael', 'Stella', 'Victor', 'Agnes', 'Samuel', 'Lydia', 'Kevin', 'Hellen', 'James', 'Susan']
    last_names = ['Maina', 'Kiprotich', 'Njoroge', 'Kibet', 'Wanjala', 'Ndungu', 'Ochieng', 'Kiprotich', 
                  'Mutua', 'Munyua', 'Barasa', 'Wanjala', 'Kiprotich', 'Njoroge', 'Nyong\'o', 'Munyua', 'Ochieng', 'Kiprotich', 'Kiprotich', 'Maina']
    
    parties = ['UDA', 'JUBILEE', 'INDEPENDENT', 'KANU', 'DAP-K', 'PNU', 'WIPER', 'ODM']
    
    created_count = 0
    error_count = 0
    
    for i, ward in enumerate(target_wards):
        try:
            # Create first candidate for this ward
            candidate1_name = f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}"
            party1 = parties[i % len(parties)]
            
            candidate1 = Candidate.objects.create(
                first_name=first_names[i % len(first_names)],
                last_name=last_names[i % len(last_names)],
                county=ward.constituency.county,
                constituency=ward.constituency,
                ward=ward,
                position=mca_position,
                party=Party.objects.get_or_create(name=party1)[0],
                id_number=f'MCA{ward.code}1'
            )
            created_count += 1
            
            # Create second candidate for this ward
            candidate2_name = f"{first_names[(i+1) % len(first_names)]} {last_names[(i+1) % len(last_names)]}"
            party2 = parties[(i+1) % len(parties)]
            
            candidate2 = Candidate.objects.create(
                first_name=first_names[(i+1) % len(first_names)],
                last_name=last_names[(i+1) % len(last_names)],
                county=ward.constituency.county,
                constituency=ward.constituency,
                ward=ward,
                position=mca_position,
                party=Party.objects.get_or_create(name=party2)[0],
                id_number=f'MCA{ward.code}2'
            )
            created_count += 1
            
            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1} wards, created {created_count} candidates...")
                
        except Exception as e:
            error_count += 1
            print(f"Error creating candidates for ward {ward.name}: {e}")
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Target wards: 1,450")
    print(f"Wards processed: {target_wards.count()}")
    print(f"Candidates created: {created_count}")
    print(f"Errors encountered: {error_count}")
    
    # Verify final count
    final_mca_count = Candidate.objects.filter(position=mca_position).count()
    final_wards_with_mcas = Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward').distinct().count()
    
    print(f"\n=== VERIFICATION ===")
    print(f"Final MCA candidate count: {final_mca_count}")
    print(f"Wards with candidates: {final_wards_with_mcas}")
    print(f"Target was: 2,900 candidates across 1,450 wards")
    
    if final_mca_count == 2900 and final_wards_with_mcas == 1450:
        print("✅ SUCCESS: Target achieved!")
    else:
        print("❌ Target not achieved. Need to investigate.")
    
    return final_mca_count, final_wards_with_mcas

if __name__ == '__main__':
    fix_mca_candidates()
