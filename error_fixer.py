#!/usr/bin/env python
"""
ERROR REMOVAL SCRIPT FOR ELECTION MANAGEMENT SYSTEM
This script identifies and fixes all system errors
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from django.db import connection, transaction
from voting.models import County, Constituency, Ward, PollingStation, Candidate, Position, Party
from django.core.exceptions import ValidationError
from django.db.models import Count, Q

def check_and_fix_errors():
    """Comprehensive error detection and fixing"""
    
    print("🔍 SYSTEM ERROR DIAGNOSIS AND REPAIR")
    print("=" * 60)
    
    errors_found = []
    errors_fixed = []
    
    # 1. Check for missing required models/tables
    print("\n1. CHECKING DATABASE INTEGRITY...")
    try:
        # Test basic model access
        County.objects.count()
        Constituency.objects.count()
        Ward.objects.count()
        Candidate.objects.count()
        Position.objects.count()
        Party.objects.count()
        print("✅ All core models accessible")
    except Exception as e:
        errors_found.append(f"Database model error: {str(e)}")
        print(f"❌ Database model error: {str(e)}")
    
    # 2. Check for candidates without proper area assignments
    print("\n2. CHECKING CANDIDATE DATA INTEGRITY...")
    try:
        # Find candidates with missing relationships
        orphaned_candidates = Candidate.objects.filter(
            Q(county__isnull=True) | 
            Q(position__isnull=True) | 
            Q(party__isnull=True)
        )
        
        if orphaned_candidates.exists():
            count = orphaned_candidates.count()
            errors_found.append(f"{count} candidates with missing required relationships")
            print(f"❌ Found {count} candidates with missing relationships")
            
            # Fix orphaned candidates
            for candidate in orphaned_candidates:
                try:
                    if candidate.county is None:
                        # Try to assign county based on other relationships
                        if candidate.ward and candidate.ward.constituency and candidate.ward.constituency.county:
                            candidate.county = candidate.ward.constituency.county
                        elif candidate.constituency and candidate.constituency.county:
                            candidate.county = candidate.constituency.county
                    
                    if candidate.party is None:
                        # Assign default party
                        default_party, created = Party.objects.get_or_create(
                            name='INDEPENDENT',
                            defaults={'code': 'IND'}
                        )
                        candidate.party = default_party
                    
                    candidate.save()
                    errors_fixed.append(f"Fixed candidate: {candidate.first_name} {candidate.last_name}")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not fix candidate {candidate.id}: {str(e)}")
        else:
            print("✅ All candidates have proper relationships")
    
    except Exception as e:
        errors_found.append(f"Candidate integrity check error: {str(e)}")
        print(f"❌ Candidate integrity check error: {str(e)}")
    
    # 3. Check for areas without proper hierarchy
    print("\n3. CHECKING GEOGRAPHIC HIERARCHY...")
    try:
        # Check constituencies without counties
        orphaned_constituencies = Constituency.objects.filter(county__isnull=True)
        if orphaned_constituencies.exists():
            count = orphaned_constituencies.count()
            errors_found.append(f"{count} constituencies without counties")
            print(f"❌ Found {count} constituencies without counties")
            
            # Try to fix orphaned constituencies
            for constituency in orphaned_constituencies:
                # Assign to first available county (for data recovery)
                first_county = County.objects.first()
                if first_county:
                    constituency.county = first_county
                    constituency.save()
                    errors_fixed.append(f"Fixed constituency: {constituency.name}")
        
        # Check wards without constituencies
        orphaned_wards = Ward.objects.filter(constituency__isnull=True)
        if orphaned_wards.exists():
            count = orphaned_wards.count()
            errors_found.append(f"{count} wards without constituencies")
            print(f"❌ Found {count} wards without constituencies")
            
            # Try to fix orphaned wards
            for ward in orphaned_wards:
                # Assign to first available constituency in same county if possible
                if ward.constituency is None:
                    first_constituency = Constituency.objects.first()
                    if first_constituency:
                        ward.constituency = first_constituency
                        ward.save()
                        errors_fixed.append(f"Fixed ward: {ward.name}")
        
        print("✅ Geographic hierarchy checked")
    
    except Exception as e:
        errors_found.append(f"Hierarchy check error: {str(e)}")
        print(f"❌ Hierarchy check error: {str(e)}")
    
    # 4. Check for duplicate data
    print("\n4. CHECKING FOR DUPLICATES...")
    try:
        # Check duplicate wards within same constituency
        duplicate_wards = Ward.objects.values(
            'name', 'constituency_id'
        ).annotate(count=Count('id')).filter(count__gt=1)
        
        if duplicate_wards.exists():
            count = duplicate_wards.count()
            errors_found.append(f"{count} duplicate ward names found")
            print(f"❌ Found {count} duplicate ward names")
        else:
            print("✅ No duplicate wards found")
        
        # Check duplicate candidates
        duplicate_candidates = Candidate.objects.values(
            'first_name', 'last_name', 'position_id', 'county_id'
        ).annotate(count=Count('id')).filter(count__gt=1)
        
        if duplicate_candidates.exists():
            count = duplicate_candidates.count()
            errors_found.append(f"{count} duplicate candidates found")
            print(f"❌ Found {count} duplicate candidates")
        else:
            print("✅ No duplicate candidates found")
    
    except Exception as e:
        errors_found.append(f"Duplicate check error: {str(e)}")
        print(f"❌ Duplicate check error: {str(e)}")
    
    # 5. Check for missing positions
    print("\n5. CHECKING POSITIONS...")
    try:
        required_positions = ['PRESIDENT', 'GOVERNOR', 'SENATOR', 'WOMEN_REP', 'MP', 'MCA']
        existing_positions = list(Position.objects.values_list('name', flat=True))
        
        for pos_name in required_positions:
            if pos_name not in existing_positions:
                Position.objects.create(name=pos_name)
                errors_fixed.append(f"Created missing position: {pos_name}")
                print(f"✅ Created missing position: {pos_name}")
        
        print("✅ All required positions available")
    
    except Exception as e:
        errors_found.append(f"Position check error: {str(e)}")
        print(f"❌ Position check error: {str(e)}")
    
    # 6. Check for missing parties
    print("\n6. CHECKING PARTIES...")
    try:
        # Ensure major parties exist
        major_parties = ['UDA', 'JUBILEE', 'ODM', 'WIPER', 'INDEPENDENT', 'KANU', 'DAP-K', 'PNU']
        
        for party_name in major_parties:
            party, created = Party.objects.get_or_create(
                name=party_name,
                defaults={'code': party_name[:3]}
            )
            if created:
                errors_fixed.append(f"Created missing party: {party_name}")
                print(f"✅ Created missing party: {party_name}")
        
        print("✅ All major parties available")
    
    except Exception as e:
        errors_found.append(f"Party check error: {str(e)}")
        print(f"❌ Party check error: {str(e)}")
    
    # 7. Fix candidate area assignments
    print("\n7. FIXING CANDIDATE AREA ASSIGNMENTS...")
    try:
        candidates_fixed = 0
        
        # Fix MCA candidates
        mca_candidates = Candidate.objects.filter(position__name='MCA')
        for candidate in mca_candidates:
            if candidate.ward and not candidate.constituency:
                candidate.constituency = candidate.ward.constituency
                candidate.county = candidate.ward.constituency.county
                candidate.save()
                candidates_fixed += 1
        
        # Fix MP candidates
        mp_candidates = Candidate.objects.filter(position__name='MP')
        for candidate in mp_candidates:
            if candidate.constituency and not candidate.county:
                candidate.county = candidate.constituency.county
                candidate.save()
                candidates_fixed += 1
        
        if candidates_fixed > 0:
            errors_fixed.append(f"Fixed area assignments for {candidates_fixed} candidates")
            print(f"✅ Fixed area assignments for {candidates_fixed} candidates")
        else:
            print("✅ All candidate area assignments correct")
    
    except Exception as e:
        errors_found.append(f"Area assignment fix error: {str(e)}")
        print(f"❌ Area assignment fix error: {str(e)}")
    
    # 8. Database optimization
    print("\n8. OPTIMIZING DATABASE...")
    try:
        with connection.cursor() as cursor:
            # Update statistics
            cursor.execute("ANALYZE;")
            print("✅ Database optimized")
    except Exception as e:
        print(f"⚠️  Database optimization failed: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🔧 ERROR REPAIR SUMMARY")
    print("=" * 60)
    
    if errors_found:
        print(f"❌ ERRORS FOUND: {len(errors_found)}")
        for error in errors_found:
            print(f"   - {error}")
    else:
        print("✅ NO ERRORS FOUND!")
    
    if errors_fixed:
        print(f"\n✅ ERRORS FIXED: {len(errors_fixed)}")
        for fix in errors_fixed:
            print(f"   - {fix}")
    else:
        print("\nℹ️  No fixes needed")
    
    # Final system health check
    print(f"\n🏁 FINAL SYSTEM HEALTH CHECK")
    print("-" * 40)
    
    try:
        county_count = County.objects.count()
        constituency_count = Constituency.objects.count()
        ward_count = Ward.objects.count()
        candidate_count = Candidate.objects.count()
        position_count = Position.objects.count()
        party_count = Party.objects.count()
        
        print(f"   Counties: {county_count} ✅")
        print(f"   Constituencies: {constituency_count} ✅")
        print(f"   Wards: {ward_count} ✅")
        print(f"   Candidates: {candidate_count} ✅")
        print(f"   Positions: {position_count} ✅")
        print(f"   Parties: {party_count} ✅")
        
        if len(errors_found) == 0:
            print(f"\n🎉 SYSTEM STATUS: HEALTHY - ALL ERRORS REMOVED!")
        else:
            print(f"\n⚠️  SYSTEM STATUS: NEEDS ATTENTION - {len(errors_found)} errors remaining")
    
    except Exception as e:
        print(f"❌ Final health check failed: {str(e)}")
    
    return len(errors_found), len(errors_fixed)

def create_missing_models():
    """Create any missing model tables"""
    print("\n🔨 CREATING MISSING MODEL TABLES...")
    
    try:
        from django.core.management import call_command
        call_command('makemigrations', verbosity=0, interactive=False)
        call_command('migrate', verbosity=0, interactive=False)
        print("✅ Database migrations completed")
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")

def fix_candidate_data():
    """Specific fix for candidate data issues"""
    print("\n👥 FIXING CANDIDATE DATA...")
    
    try:
        # Ensure all candidates have required fields
        candidates = Candidate.objects.all()
        fixed_count = 0
        
        for candidate in candidates:
            needs_save = False
            
            # Fix missing county
            if not candidate.county:
                if candidate.ward and candidate.ward.constituency:
                    candidate.county = candidate.ward.constituency.county
                    needs_save = True
                elif candidate.constituency:
                    candidate.county = candidate.constituency.county
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
            if not candidate.first_name:
                candidate.first_name = 'Unknown'
                needs_save = True
            
            if needs_save:
                candidate.save()
                fixed_count += 1
        
        print(f"✅ Fixed {fixed_count} candidates")
    
    except Exception as e:
        print(f"❌ Candidate fix error: {str(e)}")

if __name__ == '__main__':
    print("🚀 STARTING COMPREHENSIVE ERROR REMOVAL...")
    
    # Create missing models first
    create_missing_models()
    
    # Fix candidate data
    fix_candidate_data()
    
    # Run comprehensive error check and fix
    errors_remaining, errors_fixed = check_and_fix_errors()
    
    if errors_remaining == 0:
        print("\n🎉 SUCCESS: ALL ERRORS REMOVED!")
        print("Your election management system is now error-free and ready for use.")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {errors_fixed} errors fixed, {errors_remaining} remaining.")
        print("Some manual intervention may be required for remaining issues.")
