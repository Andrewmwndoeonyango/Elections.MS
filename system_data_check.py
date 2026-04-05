#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import County, Constituency, Ward, Position, Candidate, Party
from django.db.models import Count, Q

def system_data_check():
    print("=" * 60)
    print("COMPREHENSIVE ELECTION DATA SYSTEM CHECK")
    print("=" * 60)
    
    # Check Counties
    print("\n1. COUNTIES CHECK")
    print("-" * 30)
    total_counties = County.objects.count()
    print(f"Total counties: {total_counties}")
    
    counties_without_constituencies = County.objects.annotate(const_count=Count('constituency')).filter(const_count=0)
    print(f"Counties without constituencies: {counties_without_constituencies.count()}")
    if counties_without_constituencies.exists():
        for county in counties_without_constituencies:
            print(f"  - {county.name}")
    
    # Check Constituencies
    print("\n2. CONSTITUENCIES CHECK")
    print("-" * 30)
    total_constituencies = Constituency.objects.count()
    print(f"Total constituencies: {total_constituencies}")
    
    constituencies_without_wards = Constituency.objects.annotate(ward_count=Count('ward')).filter(ward_count=0)
    print(f"Constituencies without wards: {constituencies_without_wards.count()}")
    if constituencies_without_wards.exists():
        for constituency in constituencies_without_wards[:10]:
            print(f"  - {constituency.name} ({constituency.county.name})")
    
    # Check Wards
    print("\n3. WARDS CHECK")
    print("-" * 30)
    total_wards = Ward.objects.count()
    print(f"Total wards: {total_wards}")
    
    wards_without_code = Ward.objects.filter(Q(code__isnull=True) | Q(code=''))
    print(f"Wards without codes: {wards_without_code.count()}")
    
    # Check Positions
    print("\n4. POSITIONS CHECK")
    print("-" * 30)
    positions = Position.objects.all()
    print(f"Total positions: {positions.count()}")
    for position in positions:
        print(f"  - {position.name}")
    
    # Check Parties
    print("\n5. PARTIES CHECK")
    print("-" * 30)
    total_parties = Party.objects.count()
    print(f"Total parties: {total_parties}")
    
    parties_without_candidates = Party.objects.annotate(candidate_count=Count('candidate')).filter(candidate_count=0)
    print(f"Parties without candidates: {parties_without_candidates.count()}")
    
    # Check Candidates by Position
    print("\n6. CANDIDATES BY POSITION CHECK")
    print("-" * 30)
    for position in positions:
        candidates = Candidate.objects.filter(position=position)
        total = candidates.count()
        
        # Check for missing required fields
        missing_first_name = candidates.filter(Q(first_name__isnull=True) | Q(first_name='')).count()
        missing_last_name = candidates.filter(Q(last_name__isnull=True) | Q(last_name='')).count()
        missing_county = candidates.filter(county__isnull=True).count()
        missing_constituency = candidates.filter(constituency__isnull=True).count()
        missing_ward = candidates.filter(ward__isnull=True).count()
        missing_party = candidates.filter(party__isnull=True).count()
        missing_id_number = candidates.filter(Q(id_number__isnull=True) | Q(id_number='')).count()
        
        print(f"\n{position.name}: {total} candidates")
        if missing_first_name > 0:
            print(f"  ⚠️  Missing first name: {missing_first_name}")
        if missing_last_name > 0:
            print(f"  ⚠️  Missing last name: {missing_last_name}")
        if missing_county > 0:
            print(f"  ⚠️  Missing county: {missing_county}")
        if missing_constituency > 0:
            print(f"  ⚠️  Missing constituency: {missing_constituency}")
        if missing_ward > 0:
            print(f"  ⚠️  Missing ward: {missing_ward}")
        if missing_party > 0:
            print(f"  ⚠️  Missing party: {missing_party}")
        if missing_id_number > 0:
            print(f"  ⚠️  Missing ID number: {missing_id_number}")
        
        if missing_first_name == 0 and missing_last_name == 0 and missing_county == 0 and missing_constituency == 0 and missing_ward == 0 and missing_party == 0 and missing_id_number == 0:
            print(f"  ✅ All required fields complete")
    
    # Check for duplicate ID numbers
    print("\n7. DUPLICATE ID NUMBERS CHECK")
    print("-" * 30)
    duplicate_ids = Candidate.objects.values('id_number').annotate(count=Count('id')).filter(count__gt=1)
    print(f"Candidates with duplicate ID numbers: {duplicate_ids.count()}")
    if duplicate_ids.exists():
        print("⚠️  Duplicate ID numbers found:")
        for dup in duplicate_ids[:5]:
            print(f"  - {dup['id_number']}: {dup['count']} entries")
    
    # Check county coverage
    print("\n8. COUNTY COVERAGE CHECK")
    print("-" * 30)
    for position in positions:
        counties_with_candidates = Candidate.objects.filter(position=position).values('county').distinct().count()
        coverage_percentage = (counties_with_candidates / total_counties) * 100
        print(f"{position.name}: {counties_with_candidates}/{total_counties} counties ({coverage_percentage:.1f}%)")
    
    # Check wards without MCA candidates
    print("\n9. WARDS WITHOUT MCA CANDIDATES")
    print("-" * 30)
    mca_position = Position.objects.get(name='MCA')
    wards_with_mcas = Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward').distinct().count()
    wards_without_mcas = total_wards - wards_with_mcas
    print(f"Wards without MCA candidates: {wards_without_mcas}/{total_wards}")
    
    if wards_without_mcas > 0:
        print("⚠️  Some wards lack MCA candidates")
        # Show some examples
        missing_wards = Ward.objects.exclude(id__in=Candidate.objects.filter(position=mca_position, ward__isnull=False).values('ward'))
        print("Sample wards without MCA candidates:")
        for ward in missing_wards[:10]:
            print(f"  - {ward.name} ({ward.constituency.name}, {ward.constituency.county.name})")
    
    # Summary
    print("\n" + "=" * 60)
    print("SYSTEM HEALTH SUMMARY")
    print("=" * 60)
    
    issues_found = []
    
    if counties_without_constituencies.exists():
        issues_found.append(f"{counties_without_constituencies.count()} counties without constituencies")
    
    if constituencies_without_wards.exists():
        issues_found.append(f"{constituencies_without_wards.count()} constituencies without wards")
    
    if wards_without_code.exists():
        issues_found.append(f"{wards_without_code.count()} wards without codes")
    
    if duplicate_ids.exists():
        issues_found.append(f"{duplicate_ids.count()} duplicate ID numbers")
    
    if wards_without_mcas > 0:
        issues_found.append(f"{wards_without_mcas} wards without MCA candidates")
    
    if not issues_found:
        print("✅ SYSTEM HEALTH: EXCELLENT")
        print("No critical issues found in the election data.")
    else:
        print("⚠️  SYSTEM HEALTH: NEEDS ATTENTION")
        print("Issues found:")
        for issue in issues_found:
            print(f"  - {issue}")
    
    return len(issues_found)

if __name__ == '__main__':
    system_data_check()
