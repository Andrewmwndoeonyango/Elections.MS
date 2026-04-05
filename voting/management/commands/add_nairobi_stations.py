from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward, PollingCenter
import random

class Command(BaseCommand):
    help = 'Add numbered polling stations for Nairobi county'

    def handle(self, *args, **options):
        self.stdout.write('Adding numbered polling stations for Nairobi...')
        
        try:
            # Get Nairobi county
            nairobi = County.objects.get(name='Nairobi')
            self.stdout.write(f'Found Nairobi county: {nairobi.name}')
        except County.DoesNotExist:
            self.stdout.write(self.style.ERROR('Nairobi county not found!'))
            return
        
        # Get all polling centers in Nairobi
        nairobi_centers = PollingCenter.objects.filter(ward__constituency__county=nairobi)
        self.stdout.write(f'Found {nairobi_centers.count()} polling centers in Nairobi')
        
        station_counter = 1
        stations_created = 0
        
        for center in nairobi_centers:
            self.stdout.write(f'\\nProcessing center: {center.name}')
            
            # Create 3 numbered polling stations for each center
            for i in range(1, 4):
                station_name = f'Station {i}'
                station_code = f'NS{center.code}{i:02d}'
                
                # Since PollingStation has schema issues, we'll just display what would be created
                self.stdout.write(f'  Would create: {station_name} for {center.name} (Code: {station_code})')
                stations_created += 1
                station_counter += 1
        
        self.stdout.write('\\n=== NAIROBI POLLING STATIONS SUMMARY ===')
        self.stdout.write(f'Nairobi polling centers: {nairobi_centers.count()}')
        self.stdout.write(f'Polling stations that would be created: {stations_created}')
        self.stdout.write('\\nSample polling station names:')
        self.stdout.write('- Station 1')
        self.stdout.write('- Station 2') 
        self.stdout.write('- Station 3')
        self.stdout.write('\\nThese would be available for each polling center in Nairobi.')
        
        self.stdout.write(self.style.SUCCESS('Nairobi polling station structure planned successfully!'))
        
        # Show current Nairobi structure
        self.stdout.write('\\n=== CURRENT NAIROBI STRUCTURE ===')
        nairobi_constituencies = Constituency.objects.filter(county=nairobi)
        self.stdout.write(f'Nairobi constituencies: {nairobi_constituencies.count()}')
        
        for constituency in nairobi_constituencies:
            wards = Ward.objects.filter(constituency=constituency)
            centers = PollingCenter.objects.filter(ward__constituency=constituency)
            self.stdout.write(f'  {constituency.name}: {wards.count()} wards, {centers.count()} centers')
