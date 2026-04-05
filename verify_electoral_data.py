from voting.models import County, Constituency, Ward
from django.db import models

print('=== ELECTORAL DATA IMPORT SUMMARY ===')
print()

# Overall statistics
overall_stats = Ward.objects.filter(
    registered_voters_2022__gt=0
).aggregate(
    total_voters=models.Sum('registered_voters_2022'),
    total_centers=models.Sum('polling_centers'),
    total_stations=models.Sum('polling_stations'),
    ward_count=models.Count('id')
)

print(f'Total Wards with Electoral Data: {overall_stats["ward_count"]}')
print(f'Total Registered Voters (2022): {overall_stats["total_voters"]:,}')
print(f'Total Polling Centers: {overall_stats["total_centers"]:,}')
print(f'Total Polling Stations: {overall_stats["total_stations"]:,}')
print()

# County-wise statistics
print('=== COUNTY-WISE BREAKDOWN ===')
counties = County.objects.filter(
    constituency__ward__registered_voters_2022__gt=0
).distinct().order_by('name')

for county in counties:
    county_stats = Ward.objects.filter(
        constituency__county=county,
        registered_voters_2022__gt=0
    ).aggregate(
        total_voters=models.Sum('registered_voters_2022'),
        ward_count=models.Count('id')
    )
    
    print(f'{county.name}: {county_stats["ward_count"]} wards, {county_stats["total_voters"]:,} voters')

print()

# Top 10 wards by voter count
print('=== TOP 10 WARDS BY VOTER COUNT ===')
top_wards = Ward.objects.filter(
    registered_voters_2022__gt=0
).order_by('-registered_voters_2022')[:10]

for i, ward in enumerate(top_wards, 1):
    print(f'{i}. {ward.name} ({ward.constituency.county.name}): {ward.registered_voters_2022:,} voters')

print()

# Sample verification
print('=== SAMPLE WARD DETAILS ===')
sample_wards = Ward.objects.filter(registered_voters_2022__gt=0)[:3]
for ward in sample_wards:
    print(f'{ward.name} - {ward.constituency.name}, {ward.constituency.county.name}')
    print(f'  Code: {ward.code}')
    print(f'  Voters: {ward.registered_voters_2022:,}')
    print(f'  Centers: {ward.polling_centers}, Stations: {ward.polling_stations}')
    print(f'  Avg per Center: {ward.avg_voters_per_center}, Avg per Station: {ward.avg_voters_per_station}')
    print()

print('=== IMPORT COMPLETED SUCCESSFULLY ===')
