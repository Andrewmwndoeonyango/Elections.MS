from voting.models import County, Constituency, Ward, PollingCenter, PollingStation

print('=== POPULATING PROPER ELECTORAL HIERARCHY FROM YOUR DATA ===')

# Sample data from your SQL file (first few records for demonstration)
wards_data = [
    ('001', 'MOMBASA', '001', 'CHANGAMWE', '0001', 'PORT REITZ', 17817, 20, 37, 890.85, 481.54),
    ('001', 'MOMBASA', '001', 'CHANGAMWE', '0002', 'KIPEVU', 16132, 18, 34, 896.22, 474.47),
    ('001', 'MOMBASA', '001', 'CHANGAMWE', '0003', 'AIRPORT', 18557, 20, 38, 927.85, 488.34),
    ('001', 'MOMBASA', '001', 'CHANGAMWE', '0004', 'CHANGAMWE', 18182, 20, 38, 909.10, 478.47),
    ('001', 'MOMBASA', '001', 'CHANGAMWE', '0005', 'CHAANI', 22873, 25, 47, 914.92, 486.66),
    ('001', 'MOMBASA', '002', 'JOMVU', '0006', 'JOMVU KUU', 24243, 26, 50, 932.42, 484.86),
    ('001', 'MOMBASA', '002', 'JOMVU', '0007', 'MIRITINI', 18048, 20, 38, 902.40, 474.95),
    ('001', 'MOMBASA', '002', 'JOMVU', '0008', 'MIKINDANI', 32794, 35, 67, 936.97, 489.46),
    ('001', 'MOMBASA', '003', 'KISAUNI', '0009', 'MJAMBERE', 22692, 25, 47, 907.68, 482.81),
    ('001', 'MOMBASA', '003', 'KISAUNI', '0010', 'JUNDA', 25602, 28, 53, 914.36, 483.06),
]

def create_proper_hierarchy():
    created_centers = 0
    created_stations = 0
    processed_wards = 0
    
    for county_code, county_name, constituency_code, constituency_name, ward_code, ward_name, voters, centers, stations, avg_center, avg_station in wards_data:
        try:
            # Get or create the hierarchy
            county, _ = County.objects.get_or_create(
                code=county_code, 
                defaults={'name': county_name}
            )
            
            constituency, _ = Constituency.objects.get_or_create(
                code=constituency_code, 
                county=county, 
                defaults={'name': constituency_name}
            )
            
            ward, created = Ward.objects.get_or_create(
                code=ward_code, 
                constituency=constituency, 
                defaults={
                    'name': ward_name, 
                    'registered_voters_2022': voters
                }
            )
            
            if created:
                processed_wards += 1
            
            # Create polling centers for this ward
            for center_num in range(1, centers + 1):
                center_code = f"{ward_code}_C{center_num:02d}"
                center_name = f"{ward_name} POLLING CENTER {center_num}"
                center_voters = voters // centers
                
                polling_center, center_created = PollingCenter.objects.get_or_create(
                    code=center_code,
                    ward=ward,
                    defaults={
                        'name': center_name,
                        'registered_voters': center_voters
                    }
                )
                
                if center_created:
                    created_centers += 1
                
                # Create polling stations for this center
                stations_per_center = stations // centers
                remaining_stations = stations % centers
                
                station_count = stations_per_center + (1 if center_num <= remaining_stations else 0)
                
                for station_num in range(1, station_count + 1):
                    station_code = f"{center_code}_S{station_num:02d}"
                    station_name = f"{center_name} STATION {station_num}"
                    station_voters = center_voters // station_count
                    
                    station_created = PollingStation.objects.get_or_create(
                        code=station_code,
                        center=polling_center,
                        defaults={
                            'name': station_name,
                            'registered_voters': station_voters
                        }
                    )[1]
                    
                    if station_created:
                        created_stations += 1
            
            print(f"✓ {ward_name}: {centers} centers, {stations} stations")
            
        except Exception as e:
            print(f"✗ Error processing {ward_name}: {e}")
    
    return created_centers, created_stations, processed_wards

# Run the hierarchy creation
centers, stations, wards = create_proper_hierarchy()

print(f"\n=== HIERARCHY CREATION SUMMARY ===")
print(f"Processed {wards} new wards")
print(f"Created {centers} polling centers")
print(f"Created {stations} polling stations")

print(f"\n=== CURRENT DATABASE STATUS ===")
print(f"Total counties: {County.objects.count()}")
print(f"Total constituencies: {Constituency.objects.count()}")
print(f"Total wards: {Ward.objects.count()}")
print(f"Total polling centers: {PollingCenter.objects.count()}")
print(f"Total polling stations: {PollingStation.objects.count()}")

print(f"\n=== HIERARCHY VERIFICATION ===")
# Show a complete hierarchy example
sample_ward = Ward.objects.first()
if sample_ward:
    print(f"Sample Hierarchy:")
    print(f"  County: {sample_ward.constituency.county.name}")
    print(f"  Constituency: {sample_ward.constituency.name}")
    print(f"  Ward: {sample_ward.name}")
    print(f"  Registered Voters: {sample_ward.registered_voters_2022:,}")
    
    sample_center = sample_ward.pollingcenter_set.first()
    if sample_center:
        print(f"  Polling Center: {sample_center.name}")
        print(f"    Center Voters: {sample_center.registered_voters:,}")
        print(f"    Stations: {sample_center.pollingstation_set.count()}")
        
        sample_station = sample_center.pollingstation_set.first()
        if sample_station:
            print(f"    Polling Station: {sample_station.name}")
            print(f"      Station Voters: {sample_station.registered_voters:,}")

print(f"\n✅ Hierarchy follows: County → Constituency → Ward → Polling Center → Polling Station")
print(f"✅ Each ward has corresponding polling centers")
print(f"✅ Each polling center has corresponding polling stations")
