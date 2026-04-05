from voting.models import Constituency
from django.db.models import Count

print('=== REMOVING DUPLICATE CONSTITUENCY NAMES ===')

# Find duplicates by name within each county
duplicates = Constituency.objects.values('name', 'county_id').annotate(count=Count('id')).filter(count__gt=1)
print(f'Found {duplicates.count()} duplicate constituency names')

removed_count = 0

for duplicate in duplicates:
    name = duplicate['name']
    county_id = duplicate['county_id']
    
    # Get all constituencies with this name in this county
    const_list = Constituency.objects.filter(name=name, county_id=county_id).order_by('id')
    
    if const_list.count() > 1:
        # Keep the first one, delete the rest
        to_keep = const_list.first()
        to_delete = const_list[1:]
        
        print(f'Removing {to_delete.count()} duplicates of "{name}"')
        
        for const in to_delete:
            # Check if it has wards before deleting
            ward_count = const.ward_set.count()
            if ward_count > 0:
                print(f'  Warning: {const.name} has {ward_count} wards - moving them to {to_keep.name}')
                # Move wards to the kept constituency
                const.ward_set.update(constituency=to_keep)
            
            const.delete()
            removed_count += 1

print(f'\n=== RESULTS ===')
print(f'Removed {removed_count} duplicate constituencies')
print(f'Remaining constituencies: {Constituency.objects.count()}')

if Constituency.objects.count() > 290:
    print(f'\nStill have {Constituency.objects.count() - 290} extra constituencies')
    print('Checking for other duplicates...')
    
    # Show remaining potential issues
    remaining = Constituency.objects.all()
    print(f'\nSample remaining constituencies:')
    for const in remaining[:15]:
        print(f'{const.code}: {const.name} ({const.county.name})')

print(f'\nTarget: 290 constituencies')
print(f'Current: {Constituency.objects.count()}')
if Constituency.objects.count() == 290:
    print('✅ PERFECT! Kenya now has correct 290 constituencies')
else:
    print(f'⚠️  Need to remove {Constituency.objects.count() - 290} more constituencies')
