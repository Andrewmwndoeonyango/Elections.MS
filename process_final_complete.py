from voting.models import County, Constituency, Ward
import csv

print('=== PROCESSING FINAL COUNTIES: LAIKIPIA, NYERI, KIRINYAGA, BARINGO, SAMBURU ===')

updated = 0
created = 0
errors = 0

with open('final_counties_complete.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        county_name = row['county_name'].strip().title()
        constituency_name = row['constituency_name'].strip()
        ward_name = row['ward_name'].strip()
        ward_code = row['ward_code'].strip()
        
        try:
            # Get existing county
            county = County.objects.get(name__iexact=county_name)
            
            # Get or create constituency
            constituency, _ = Constituency.objects.get_or_create(
                name=constituency_name,
                county=county,
                defaults={'code': row['constituency_code']}
            )
            
            # Update or create ward
            ward, created_ward = Ward.objects.update_or_create(
                code=ward_code,
                constituency=constituency,
                defaults={
                    'name': ward_name,
                    'registered_voters_2022': int(row['ward_registered_voters_2022']),
                    'polling_centers': int(row['allocated_polling_centers']),
                    'polling_stations': int(row['allocated_polling_stations']),
                    'avg_voters_per_center': float(row['avg_voters_per_center_est']),
                    'avg_voters_per_station': float(row['avg_voters_per_station_est'])
                }
            )
            
            if created_ward:
                created += 1
            else:
                updated += 1
                
            if (created + updated) % 40 == 0:
                print(f'Processed {created + updated} wards...')
                
        except County.DoesNotExist:
            errors += 1
            print(f'County not found: {county_name}')
        except Exception as e:
            errors += 1
            print(f'Error: {str(e)}')

print(f'\n=== SUMMARY ===')
print(f'Wards updated: {updated}')
print(f'Wards created: {created}')
print(f'Errors: {errors}')
print(f'Total wards now: {Ward.objects.count()}')

# Updated statistics
from django.db import models
total_voters = Ward.objects.aggregate(total=models.Sum('registered_voters_2022'))['total'] or 0
wards_with_data = Ward.objects.exclude(registered_voters_2022=0).count()

print(f'\n=== UPDATED ELECTORAL STATISTICS ===')
print(f'Wards with electoral data: {wards_with_data}')
print(f'Total registered voters: {total_voters:,}')

# Final verification
counties_completed = County.objects.filter(
    constituency__ward__registered_voters_2022__gt=0
).distinct().count()

print(f'\n=== FINAL STATUS ===')
print(f'Counties completed: {counties_completed}/47')
print(f'Wards with electoral data: {wards_with_data}')
print(f'Total registered voters: {total_voters:,}')

if counties_completed == 47:
    print('\n🎉 ELECTORAL DATA IMPORT COMPLETED SUCCESSFULLY! 🎉')
else:
    remaining = 47 - counties_completed
    print(f'\n⚠️  {remaining} counties still need data')
