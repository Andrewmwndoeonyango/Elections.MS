from django.db import models
from voting.models import County, Constituency, Ward
import csv
import django
import os

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()


def update_wards_with_electoral_data():
    print('=== UPDATING WARDS WITH OFFICIAL NAMES AND ELECTORAL DATA ===')

    # Read the CSV file
    with open('electoral_data.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        updated_count = 0
        created_count = 0
        error_count = 0

        for row in reader:
            try:
                county_name = row['county_name'].strip()
                constituency_name = row['constituency_name'].strip()
                ward_name = row['ward_name'].strip()
                ward_code = row['ward_code'].strip()

                # Get or create county
                county, created = County.objects.get_or_create(
                    name=county_name,
                    defaults={'code': row['county_code']}
                )
                if created:
                    print(f'Created county: {county_name}')

                # Get or create constituency
                constituency, created = Constituency.objects.get_or_create(
                    name=constituency_name,
                    county=county,
                    defaults={'code': row['constituency_code']}
                )
                if created:
                    print(f'Created constituency: {constituency_name}')

                # Try to find existing ward by code (if any match)
                existing_ward = Ward.objects.filter(
                    constituency__county=county,
                    constituency__name__icontains=constituency_name
                ).first()

                if existing_ward:
                    # Update existing ward with official name and data
                    existing_ward.name = ward_name
                    existing_ward.code = ward_code
                    existing_ward.registered_voters_2022 = int(
                        row['ward_registered_voters_2022'])
                    existing_ward.polling_centers = int(
                        row['allocated_polling_centers'])
                    existing_ward.polling_stations = int(
                        row['allocated_polling_stations'])
                    existing_ward.avg_voters_per_center = float(
                        row['avg_voters_per_center_est'])
                    existing_ward.avg_voters_per_station = float(
                        row['avg_voters_per_station_est'])
                    existing_ward.save()
                    updated_count += 1

                    if updated_count % 10 == 0:
                        print(f'Updated {updated_count} wards...')

                else:
                    # Create new ward
                    ward = Ward.objects.create(
                        name=ward_name,
                        code=ward_code,
                        constituency=constituency,
                        registered_voters_2022=int(
                            row['ward_registered_voters_2022']),
                        polling_centers=int(row['allocated_polling_centers']),
                        polling_stations=int(
                            row['allocated_polling_stations']),
                        avg_voters_per_center=float(
                            row['avg_voters_per_center_est']),
                        avg_voters_per_station=float(
                            row['avg_voters_per_station_est'])
                    )
                    created_count += 1

                    if created_count % 10 == 0:
                        print(f'Created {created_count} wards...')

            except Exception as e:
                error_count += 1
                print(f'Error processing {row["ward_name"]}: {str(e)}')

        print(f'\n=== SUMMARY ===')
        print(f'Wards updated: {updated_count}')
        print(f'Wards created: {created_count}')
        print(f'Errors: {error_count}')
        print(f'Total wards in system: {Ward.objects.count()}')

        # Show statistics
        print(f'\n=== ELECTORAL STATISTICS ===')
        total_voters = Ward.objects.aggregate(
            total=models.Sum('registered_voters_2022')
        )['total'] or 0
        total_centers = Ward.objects.aggregate(
            total=models.Sum('polling_centers')
        )['total'] or 0
        total_stations = Ward.objects.aggregate(
            total=models.Sum('polling_stations')
        )['total'] or 0

        print(f'Total registered voters (2022): {total_voters:,}')
        print(f'Total polling centers: {total_centers:,}')
        print(f'Total polling stations: {total_stations:,}')

        # Verify some data
        print(f'\n=== SAMPLE VERIFICATION ===')
        sample_wards = Ward.objects.exclude(registered_voters_2022=0)[:5]
        for ward in sample_wards:
            print(f'{ward.name} ({ward.constituency.name}, {ward.constituency.county.name}): '
                  f'{ward.registered_voters_2022:,} voters, {ward.polling_centers} centers')


if __name__ == '__main__':
    update_wards_with_electoral_data()
