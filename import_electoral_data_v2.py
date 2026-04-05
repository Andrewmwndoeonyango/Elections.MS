import csv
import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import County, Constituency, Ward

def import_electoral_data_by_name():
    print('=== IMPORTING ELECTORAL DATA BY NAME MATCHING ===')
    
    # Read the CSV file
    with open('electoral_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        updated_count = 0
        not_found_count = 0
        multiple_matches_count = 0
        
        for row in reader:
            ward_name = row['ward_name'].strip()
            constituency_name = row['constituency_name'].strip()
            county_name = row['county_name'].strip()
            
            try:
                # Try to find ward by exact name match
                wards = Ward.objects.filter(name__iexact=ward_name)
                
                if wards.count() == 1:
                    ward = wards.first()
                    update_ward(ward, row)
                    updated_count += 1
                    
                elif wards.count() > 1:
                    # Multiple matches, try to narrow down by constituency
                    constituency_wards = wards.filter(constituency__name__icontains=constituency_name)
                    if constituency_wards.count() == 1:
                        ward = constituency_wards.first()
                        update_ward(ward, row)
                        updated_count += 1
                    else:
                        multiple_matches_count += 1
                        print(f'Multiple matches for {ward_name} in {constituency_name}')
                        
                else:
                    # No exact match, try partial name matching
                    partial_wards = Ward.objects.filter(name__icontains=ward_name.split()[0])
                    if partial_wards.count() == 1:
                        ward = partial_wards.first()
                        update_ward(ward, row)
                        updated_count += 1
                        print(f'Partial match: {ward.name} for {ward_name}')
                    else:
                        not_found_count += 1
                        print(f'Ward not found: {ward_name} ({constituency_name}, {county_name})')
                
                if updated_count % 10 == 0:
                    print(f'Updated {updated_count} wards...')
                    
            except Exception as e:
                print(f'Error updating {ward_name}: {str(e)}')
        
        print(f'\n=== IMPORT SUMMARY ===')
        print(f'Wards updated: {updated_count}')
        print(f'Wards not found: {not_found_count}')
        print(f'Multiple matches: {multiple_matches_count}')
        print(f'Total wards in system: {Ward.objects.count()}')
        
        # Verify some updated data
        print(f'\n=== VERIFICATION ===')
        sample_wards = Ward.objects.exclude(registered_voters_2022=0)[:5]
        for ward in sample_wards:
            print(f'{ward.name}: {ward.registered_voters_2022} voters, {ward.polling_centers} centers')

def update_ward(ward, row):
    """Update ward with electoral data"""
    ward.registered_voters_2022 = int(row['ward_registered_voters_2022'])
    ward.polling_centers = int(row['allocated_polling_centers'])
    ward.polling_stations = int(row['allocated_polling_stations'])
    ward.avg_voters_per_center = float(row['avg_voters_per_center_est'])
    ward.avg_voters_per_station = float(row['avg_voters_per_station_est'])
    ward.save()

if __name__ == '__main__':
    import_electoral_data_by_name()
