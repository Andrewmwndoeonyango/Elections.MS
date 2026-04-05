from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward, PollingCenter
import random

class Command(BaseCommand):
    help = 'Generate comprehensive random election data for all counties (up to polling center level)'

    def handle(self, *args, **options):
        self.stdout.write('Generating comprehensive election data...')
        
        # Clear existing hierarchical data (keep counties and candidates)
        PollingCenter.objects.all().delete()
        Ward.objects.all().delete()
        Constituency.objects.all().delete()
        
        self.stdout.write('Cleared existing hierarchical data')
        
        counties = County.objects.all()
        self.stdout.write(f'Processing {counties.count()} counties')
        
        constituency_counter = 1
        ward_counter = 1
        center_counter = 1
        
        for county in counties:
            self.stdout.write(f'Processing county: {county.name}')
            
            # Create 3-8 constituencies per county
            num_constituencies = random.randint(3, 8)
            
            for i in range(num_constituencies):
                constituency_name = self.get_random_constituency_name(county.name)
                constituency_code = f'C{constituency_counter:03d}'
                
                constituency = Constituency.objects.create(
                    name=constituency_name,
                    county=county,
                    code=constituency_code
                )
                constituency_counter += 1
                
                self.stdout.write(f'  Created constituency: {constituency_name}')
                
                # Create 3-6 wards per constituency
                num_wards = random.randint(3, 6)
                
                for j in range(num_wards):
                    ward_name = self.get_random_ward_name(constituency_name)
                    ward_code = f'W{ward_counter:03d}'
                    
                    ward = Ward.objects.create(
                        name=ward_name,
                        constituency=constituency,
                        code=ward_code
                    )
                    ward_counter += 1
                    
                    self.stdout.write(f'    Created ward: {ward_name}')
                    
                    # Create 1-3 polling centers per ward
                    num_centers = random.randint(1, 3)
                    
                    for k in range(num_centers):
                        center_name = self.get_random_polling_center_name(ward_name)
                        center_code = f'P{center_counter:03d}'
                        
                        center = PollingCenter.objects.create(
                            name=center_name,
                            ward=ward,
                            code=center_code
                        )
                        center_counter += 1
                        
                        self.stdout.write(f'      Created center: {center_name}')
        
        self.stdout.write('\\n=== FINAL DATA SUMMARY ===')
        self.stdout.write(f'Counties: {County.objects.count()}')
        self.stdout.write(f'Constituencies: {Constituency.objects.count()}')
        self.stdout.write(f'Wards: {Ward.objects.count()}')
        self.stdout.write(f'Polling Centers: {PollingCenter.objects.count()}')
        self.stdout.write('Note: Polling stations will be created on-demand during registration')
        
        self.stdout.write(self.style.SUCCESS('Comprehensive election data generated successfully!'))
    
    def get_random_constituency_name(self, county_name):
        prefixes = ['North', 'South', 'East', 'West', 'Central', 'Upper', 'Lower', 'New', 'Old', 'Greater']
        suffixes = ['Town', 'City', 'Hills', 'Valley', 'Plains', 'Ridge', 'Grove', 'Park', 'Gardens', 'Heights']
        return f'{random.choice(prefixes)} {county_name} {random.choice(suffixes)}'
    
    def get_random_ward_name(self, constituency_name):
        ward_types = ['Central', 'North', 'South', 'East', 'West', 'Market', 'Station', 'Junction', 'Square', 'Cross']
        return f'{constituency_name} {random.choice(ward_types)}'
    
    def get_random_polling_center_name(self, ward_name):
        center_types = ['Primary School', 'Community Hall', 'Church', 'Social Hall', 'Training Center', 'Chief\'s Camp', 'Dispensary', 'Market Center']
        return f'{ward_name} {random.choice(center_types)}'
