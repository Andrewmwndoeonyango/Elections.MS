#!/usr/bin/env python
"""
CREATE RESULTS SYSTEM - Simplified Version
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from django.db import connection

def create_results_table():
    """Create results table"""
    print("Creating results table...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voting_result (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    polling_station_id INTEGER NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    votes INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (polling_station_id) REFERENCES voting_pollingstation(id),
                    FOREIGN KEY (candidate_id) REFERENCES voting_candidate(id),
                    
                    UNIQUE(polling_station_id, candidate_id),
                    CHECK (votes >= 0)
                )
            """)
            
            print("✅ Results table created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def seed_basic_results():
    """Seed basic sample results"""
    print("Seeding sample results...")
    
    try:
        from voting.models import Candidate, PollingStation
        import random
        
        # Clear existing results
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM voting_result")
        
        # Get some candidates and stations
        candidates = list(Candidate.objects.all()[:50])
        stations = list(PollingStation.objects.all()[:20])
        
        if not candidates or not stations:
            print("❌ No candidates or stations found")
            return False
        
        # Create sample results
        for candidate in candidates:
            for station in stations[:3]:  # 3 stations per candidate
                votes = random.randint(50, 500)
                
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT OR IGNORE INTO voting_result 
                        (polling_station_id, candidate_id, votes) 
                        VALUES (?, ?, ?)
                    """, [station.id, candidate.id, votes])
        
        print("✅ Sample results created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding results: {str(e)}")
        return False

def main():
    print("Creating Results System")
    print("=" * 40)
    
    success = True
    
    if not create_results_table():
        success = False
    
    if not seed_basic_results():
        success = False
    
    if success:
        print("\n✅ Results system implemented successfully!")
        print("Your system now has:")
        print("  • Results table with validation")
        print("  • Sample vote data")
        print("  • Ready for dashboard integration")
    else:
        print("\n❌ Implementation failed")

if __name__ == '__main__':
    main()
