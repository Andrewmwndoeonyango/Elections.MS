import csv
import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()

from voting.models import County, Constituency, Ward

def import_electoral_data():
    print('=== IMPORTING ELECTORAL DATA ===')
    
    # Read the CSV file
    with open('electoral_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        updated_count = 0
        not_found_count = 0
        
        for row in reader:
            try:
                # Find the ward by code
                ward_code = row['ward_code']
                ward = Ward.objects.get(code=ward_code)
                
                # Update ward with electoral data
                ward.registered_voters_2022 = int(row['ward_registered_voters_2022'])
                ward.polling_centers = int(row['allocated_polling_centers'])
                ward.polling_stations = int(row['allocated_polling_stations'])
                ward.avg_voters_per_center = float(row['avg_voters_per_center_est'])
                ward.avg_voters_per_station = float(row['avg_voters_per_station_est'])
                
                ward.save()
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f'Updated {updated_count} wards...')
                    
            except Ward.DoesNotExist:
                not_found_count += 1
                print(f'Ward not found: {row["ward_name"]} ({ward_code})')
            except Exception as e:
                print(f'Error updating {row["ward_name"]}: {str(e)}')
        
        print(f'\n=== IMPORT SUMMARY ===')
        print(f'Wards updated: {updated_count}')
        print(f'Wards not found: {not_found_count}')
        print(f'Total wards in system: {Ward.objects.count()}')
        
        # Verify some updated data
        print(f'\n=== VERIFICATION ===')
        sample_wards = Ward.objects.exclude(registered_voters_2022=0)[:5]
        for ward in sample_wards:
            print(f'{ward.name}: {ward.registered_voters_2022} voters, {ward.polling_centers} centers')

if __name__ == '__main__':
    import_electoral_data()
