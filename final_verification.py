from voting.models import County, Constituency, Ward

print('=== FINAL PROGRESS STATUS ===')
print(f'Total wards in system: {Ward.objects.count()}')
print(f'Wards with electoral data: {Ward.objects.exclude(registered_voters_2022=0).count()}')

print('\n=== COUNTIES WITH DATA ===')
counties_with_data = County.objects.filter(
    constituency__ward__registered_voters_2022__gt=0
).distinct().order_by('name')

for county in counties_with_data:
    ward_count = Ward.objects.filter(
        constituency__county=county,
        registered_voters_2022__gt=0
    ).count()
    print(f'✅ {county.name}: {ward_count} wards')

print(f'\nCounties completed: {counties_with_data.count()}/47')

print('\n=== COUNTIES STILL NEEDED ===')
counties_needed = County.objects.exclude(
    id__in=counties_with_data
).order_by('name')

for county in counties_needed:
    print(f'❌ {county.name}')

print(f'\nCounties remaining: {counties_needed.count()}')

# Overall statistics
from django.db import models
overall_stats = Ward.objects.filter(
    registered_voters_2022__gt=0
).aggregate(
    total_voters=models.Sum('registered_voters_2022'),
    total_centers=models.Sum('polling_centers'),
    total_stations=models.Sum('polling_stations'),
    ward_count=models.Count('id')
)

print(f'\n=== OVERALL KENYA ELECTORAL STATISTICS ===')
print(f'Total Wards with Data: {overall_stats["ward_count"]}')
print(f'Total Registered Voters (2022): {overall_stats["total_voters"]:,.0f}')
print(f'Total Polling Centers: {overall_stats["total_centers"]:,.0f}')
print(f'Total Polling Stations: {overall_stats["total_stations"]:,.0f}')

print('\n=== ELECTORAL DATA IMPORT COMPLETED ===')
