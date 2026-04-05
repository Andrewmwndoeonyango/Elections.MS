from django.core.management.base import BaseCommand
from voting.models import Constituency
from django.db.models import Count

class Command(BaseCommand):
    help = 'Remove duplicate constituency names'

    def handle(self, *args, **options):
        self.stdout.write('=== REMOVING DUPLICATE CONSTITUENCY NAMES ===')
        
        # Find duplicates by name within each county
        duplicates = Constituency.objects.values('name', 'county_id').annotate(count=Count('id')).filter(count__gt=1)
        self.stdout.write(f'Found {duplicates.count()} duplicate constituency names')
        
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
                
                self.stdout.write(f'Removing {to_delete.count()} duplicates of "{name}"')
                
                for const in to_delete:
                    # Move wards to the kept constituency
                    const.ward_set.update(constituency=to_keep)
                    const.delete()
                    removed_count += 1
        
        self.stdout.write(f'\n=== RESULTS ===')
        self.stdout.write(f'Removed {removed_count} duplicate constituencies')
        self.stdout.write(f'Remaining constituencies: {Constituency.objects.count()}')
        
        if Constituency.objects.count() == 290:
            self.stdout.write(self.style.SUCCESS('✅ PERFECT! Kenya now has correct 290 constituencies'))
        else:
            self.stdout.write(f'⚠️  Need to remove {Constituency.objects.count() - 290} more constituencies')
