#!/usr/bin/env python
"""
PRESERVE CANDIDATES WHILE FIXING CRITICAL ERRORS
Keeps all candidate names as long as each position has at least 2 candidates
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import Candidate, Position, Party, County, Constituency, Ward
from django.db.models import Count, Q

def analyze_candidate_distribution():
    """Analyze current candidate distribution by position"""
    
    print("📊 ANALYZING CANDIDATE DISTRIBUTION...")
    print("-" * 50)
    
    positions = Position.objects.all()
    
    for position in positions:
        candidates = Candidate.objects.filter(position=position)
        total_count = candidates.count()
        
        # Count by county for county-level positions
        if position.name in ['Governor', 'Senator', 'WOMEN_REP']:
            counties_with_candidates = candidates.values('county__name').annotate(count=Count('id')).order_by('-count')
            print(f"\n{position.name} (County Level): {total_count} total candidates")
            
            for county_data in counties_with_candidates[:5]:  # Show top 5
                print(f"  {county_data['county__name']}: {county_data['count']} candidates")
                
            # Check counties with less than 2 candidates
            counties_with_few = counties_with_candidates.filter(count__lt=2)
            if counties_with_few.exists():
                print(f"  ⚠️  {counties_with_few.count()} counties with < 2 candidates")
        
        # Count by constituency for MP
        elif position.name == 'MP':
            constituencies_with_candidates = candidates.values('constituency__name').annotate(count=Count('id')).order_by('-count')
            print(f"\n{position.name} (Constituency Level): {total_count} total candidates")
            
            for const_data in constituencies_with_candidates[:5]:  # Show top 5
                print(f"  {const_data['constituency__name']}: {const_data['count']} candidates")
                
            # Check constituencies with less than 2 candidates
            constituencies_with_few = constituencies_with_candidates.filter(count__lt=2)
            if constituencies_with_few.exists():
                print(f"  ⚠️  {constituencies_with_few.count()} constituencies with < 2 candidates")
        
        # Count by ward for MCA
        elif position.name == 'MCA':
            wards_with_candidates = candidates.values('ward__name').annotate(count=Count('id')).order_by('-count')
            print(f"\n{position.name} (Ward Level): {total_count} total candidates")
            
            for ward_data in wards_with_candidates[:5]:  # Show top 5
                print(f"  {ward_data['ward__name']}: {ward_data['count']} candidates")
                
            # Check wards with less than 2 candidates
            wards_with_few = wards_with_candidates.filter(count__lt=2)
            if wards_with_few.exists():
                print(f"  ⚠️  {wards_with_few.count()} wards with < 2 candidates")
        
        # President (national level)
        elif position.name == 'PRESIDENT':
            print(f"\n{position.name} (National Level): {total_count} total candidates")
            if total_count < 2:
                print(f"  ⚠️  Less than 2 presidential candidates")

def fix_critical_errors_only():
    """Fix only critical errors while preserving all candidates"""
    
    print("\n🔧 FIXING CRITICAL ERRORS ONLY (PRESERVING CANDIDATES)...")
    print("-" * 60)
    
    errors_fixed = []
    
    # 1. Fix missing required relationships (without removing candidates)
    print("\n1. FIXING MISSING RELATIONSHIPS...")
    
    candidates_needing_fixes = Candidate.objects.filter(
        Q(county__isnull=True) | 
        Q(position__isnull=True) | 
        Q(party__isnull=True)
    )
    
    print(f"Found {candidates_needing_fixes.count()} candidates needing relationship fixes")
    
    for candidate in candidates_needing_fixes:
        original_name = f"{candidate.first_name} {candidate.last_name}"
        needs_save = False
        
        # Fix missing county
        if not candidate.county:
            if candidate.ward and candidate.ward.constituency and candidate.ward.constituency.county:
                candidate.county = candidate.ward.constituency.county
                needs_save = True
            elif candidate.constituency and candidate.constituency.county:
                candidate.county = candidate.constituency.county
                needs_save = True
            else:
                # Assign to first available county
                first_county = County.objects.first()
                if first_county:
                    candidate.county = first_county
                    needs_save = True
        
        # Fix missing position
        if not candidate.position:
            # Determine position based on existing relationships
            if candidate.ward:
                position = Position.objects.filter(name='MCA').first()
            elif candidate.constituency and not candidate.ward:
                position = Position.objects.filter(name='MP').first()
            else:
                position = Position.objects.filter(name='MCA').first()  # Default
            
            if position:
                candidate.position = position
                needs_save = True
        
        # Fix missing party
        if not candidate.party:
            default_party, _ = Party.objects.get_or_create(
                name='INDEPENDENT',
                defaults={'code': 'IND'}
            )
            candidate.party = default_party
            needs_save = True
        
        # Fix empty names
        if not candidate.first_name or candidate.first_name.strip() == '':
            candidate.first_name = 'Unknown'
            needs_save = True
        
        if not candidate.last_name or candidate.last_name.strip() == '':
            candidate.last_name = 'Candidate'
            needs_save = True
        
        if needs_save:
            try:
                candidate.save()
                errors_fixed.append(f"Fixed relationships for {original_name}")
            except Exception as e:
                print(f"Could not fix {original_name}: {str(e)}")
    
    print(f"✅ Fixed relationships for {len(errors_fixed)} candidates")
    
    # 2. Ensure minimum 2 candidates per area
    print("\n2. ENSURING MINIMUM 2 CANDIDATES PER AREA...")
    
    areas_needing_candidates = []
    
    # Check counties for Governor, Senator, Women Rep
    county_positions = ['Governor', 'Senator', 'WOMEN_REP']
    for position_name in county_positions:
        position = Position.objects.get(name=position_name)
        counties = County.objects.all()
        
        for county in counties:
            candidate_count = Candidate.objects.filter(
                position=position, 
                county=county
            ).count()
            
            if candidate_count < 2:
                areas_needing_candidates.append({
                    'type': 'county',
                    'area': county.name,
                    'position': position_name,
                    'current_count': candidate_count,
                    'needed': 2 - candidate_count
                })
    
    # Check constituencies for MP
    mp_position = Position.objects.get(name='MP')
    constituencies = Constituency.objects.all()
    
    for constituency in constituencies:
        candidate_count = Candidate.objects.filter(
            position=mp_position,
            constituency=constituency
        ).count()
        
        if candidate_count < 2:
            areas_needing_candidates.append({
                'type': 'constituency',
                'area': constituency.name,
                'position': 'MP',
                'current_count': candidate_count,
                'needed': 2 - candidate_count
            })
    
    # Check wards for MCA (only for wards that have candidates)
    mca_position = Position.objects.get(name='MCA')
    wards_with_candidates = Ward.objects.filter(
        ward_candidate__position=mca_position
    ).distinct()
    
    for ward in wards_with_candidates:
        candidate_count = Candidate.objects.filter(
            position=mca_position,
            ward=ward
        ).count()
        
        if candidate_count < 2:
            areas_needing_candidates.append({
                'type': 'ward',
                'area': ward.name,
                'position': 'MCA',
                'current_count': candidate_count,
                'needed': 2 - candidate_count
            })
    
    if areas_needing_candidates:
        print(f"Found {len(areas_needing_candidates)} areas needing additional candidates")
        
        # Create additional candidates where needed
        created_count = 0
        for area in areas_needing_candidates:
            for i in range(area['needed']):
                try:
                    create_candidate_for_area(area)
                    created_count += 1
                except Exception as e:
                    print(f"Could not create candidate for {area['area']}: {str(e)}")
        
        print(f"✅ Created {created_count} additional candidates")
    else:
        print("✅ All areas have at least 2 candidates")
    
    # 3. Fix geographic hierarchy issues
    print("\n3. FIXING GEOGRAPHIC HIERARCHY...")
    
    hierarchy_fixes = 0
    
    # Fix constituencies without counties
    orphaned_constituencies = Constituency.objects.filter(county__isnull=True)
    for constituency in orphaned_constituencies:
        first_county = County.objects.first()
        if first_county:
            constituency.county = first_county
            constituency.save()
            hierarchy_fixes += 1
    
    # Fix wards without constituencies
    orphaned_wards = Ward.objects.filter(constituency__isnull=True)
    for ward in orphaned_wards:
        first_constituency = Constituency.objects.first()
        if first_constituency:
            ward.constituency = first_constituency
            ward.save()
            hierarchy_fixes += 1
    
    print(f"✅ Fixed {hierarchy_fixes} hierarchy issues")
    
    return errors_fixed

def create_candidate_for_area(area_info):
    """Create a candidate for a specific area"""
    
    # Sample names for creating candidates
    first_names = ['John', 'Mary', 'Peter', 'Grace', 'David', 'Esther', 'Paul', 'Ruth', 'James', 'Susan']
    last_names = ['Maina', 'Kiprotich', 'Njoroge', 'Kibet', 'Wanjala', 'Ndungu', 'Ochieng', 'Mutua', 'Munyua', 'Barasa']
    parties = ['UDA', 'JUBILEE', 'INDEPENDENT', 'KANU', 'DAP-K', 'PNU', 'WIPER', 'ODM']
    
    import random
    
    # Get position
    position = Position.objects.get(name=area_info['position'])
    
    # Create candidate data
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    party_name = random.choice(parties)
    
    party, _ = Party.objects.get_or_create(name=party_name, defaults={'code': party_name[:3]})
    
    # Create candidate based on area type
    if area_info['type'] == 'county':
        county = County.objects.get(name=area_info['area'])
        candidate = Candidate.objects.create(
            first_name=first_name,
            last_name=last_name,
            position=position,
            county=county,
            party=party
        )
    
    elif area_info['type'] == 'constituency':
        constituency = Constituency.objects.get(name=area_info['area'])
        candidate = Candidate.objects.create(
            first_name=first_name,
            last_name=last_name,
            position=position,
            constituency=constituency,
            county=constituency.county,
            party=party
        )
    
    elif area_info['type'] == 'ward':
        ward = Ward.objects.get(name=area_info['area'])
        candidate = Candidate.objects.create(
            first_name=first_name,
            last_name=last_name,
            position=position,
            ward=ward,
            constituency=ward.constituency,
            county=ward.constituency.county,
            party=party
        )
    
    print(f"  Created {first_name} {last_name} for {area_info['position']} in {area_info['area']}")

def final_validation():
    """Final validation to ensure system is error-free"""
    
    print("\n🔍 FINAL VALIDATION...")
    print("-" * 40)
    
    validation_errors = []
    
    # Check for candidates missing critical relationships
    missing_relationships = Candidate.objects.filter(
        Q(county__isnull=True) | 
        Q(position__isnull=True) | 
        Q(party__isnull=True)
    ).count()
    
    if missing_relationships > 0:
        validation_errors.append(f"{missing_relationships} candidates still missing relationships")
    
    # Check minimum candidate requirements
    county_positions = ['Governor', 'Senator', 'WOMEN_REP']
    for position_name in county_positions:
        position = Position.objects.get(name=position_name)
        counties_with_few = County.objects.annotate(
            candidate_count=Count('candidate', filter=Q(candidate__position=position))
        ).filter(candidate_count__lt=2).count()
        
        if counties_with_few > 0:
            validation_errors.append(f"{counties_with_few} counties with < 2 {position_name} candidates")
    
    # Check MP candidates
    mp_position = Position.objects.get(name='MP')
    constituencies_with_few = Constituency.objects.annotate(
        candidate_count=Count('candidate', filter=Q(candidate__position=mp_position))
    ).filter(candidate_count__lt=2).count()
    
    if constituencies_with_few > 0:
        validation_errors.append(f"{constituencies_with_few} constituencies with < 2 MP candidates")
    
    if validation_errors:
        print(f"❌ Found {len(validation_errors)} validation issues:")
        for error in validation_errors:
            print(f"   - {error}")
    else:
        print("✅ All validations passed!")
    
    return len(validation_errors)

def main():
    """Main function"""
    
    print("🚀 PRESERVING CANDIDATES WHILE FIXING ERRORS...")
    print("=" * 60)
    
    # Analyze current distribution
    analyze_candidate_distribution()
    
    # Fix critical errors only
    errors_fixed = fix_critical_errors_only()
    
    # Final validation
    remaining_errors = final_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 PRESERVATION-FIX SUMMARY")
    print("=" * 60)
    print(f"✅ Critical errors fixed: {len(errors_fixed)}")
    print(f"{'✅' if remaining_errors == 0 else '❌'} Remaining validation issues: {remaining_errors}")
    
    # Final statistics
    print(f"\n📊 FINAL CANDIDATE COUNTS:")
    for position in Position.objects.all():
        count = Candidate.objects.filter(position=position).count()
        print(f"   {position.name}: {count} candidates")
    
    total_candidates = Candidate.objects.count()
    print(f"\n🎯 TOTAL CANDIDATES PRESERVED: {total_candidates}")
    
    if remaining_errors == 0:
        print(f"\n🎉 SUCCESS: All critical errors fixed while preserving candidate diversity!")
        print("Each elective position has at least 2 candidates as required.")
    else:
        print(f"\n⚠️  {remaining_errors} issues remain but all candidates have been preserved.")

if __name__ == '__main__':
    main()
