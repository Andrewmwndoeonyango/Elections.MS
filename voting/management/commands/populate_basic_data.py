from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward, PollingCenter, PollingStation, Position, Party, Candidate
import random

class Command(BaseCommand):
    help = 'Populate the database with basic Kenyan election data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate basic Kenyan election data...')
        
        # Create parties
        self.create_parties()
        
        # Create positions
        self.create_positions()
        
        # Create basic counties and units
        self.create_basic_counties()
        
        # Create candidates
        self.create_basic_candidates()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated basic Kenyan election data!'))

    def create_parties(self):
        parties_data = [
            ('Jubilee Party', 'JP', 'A center-right political party in Kenya'),
            ('Orange Democratic Movement', 'ODM', 'A center-left political party in Kenya'),
            ('United Democratic Alliance', 'UDA', 'A political party in Kenya associated with William Ruto'),
            ('Wiper Democratic Movement', 'WDM', 'A political party in Kenya led by Kalonzo Musyoka'),
        ]
        
        for name, code, description in parties_data:
            Party.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        self.stdout.write('Created parties')

    def create_positions(self):
        positions = [
            ('PRESIDENT', 'President of the Republic of Kenya'),
            ('GOVERNOR', 'County Governor'),
            ('SENATOR', 'Senator'),
            ('WOMEN_REP', 'Women Representative'),
            ('MP', 'Member of Parliament'),
            ('MCA', 'Member of County Assembly'),
        ]
        
        for name, description in positions:
            Position.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        self.stdout.write('Created positions')

    def create_basic_counties(self):
        # Create a few major counties with basic structure
        counties_data = [
            ('Nairobi', '001'),
            ('Mombasa', '002'), 
            ('Kisumu', '003'),
            ('Nakuru', '004'),
            ('Kiambu', '005'),
        ]
        
        for name, code in counties_data:
            county, created = County.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            if created:
                self.create_county_units(county)
        
        self.stdout.write('Created basic counties and units')

    def create_county_units(self, county):
        # Create 3 constituencies per county
        for i in range(1, 4):
            constituency_name = f"{county.name} Constituency {i}"
            constituency, _ = Constituency.objects.get_or_create(
                name=constituency_name,
                county=county,
                defaults={'code': f"{county.code}{i:02d}"}
            )
            
            # Create 2 wards per constituency
            for j in range(1, 3):
                ward_name = f"{constituency_name} Ward {j}"
                ward, _ = Ward.objects.get_or_create(
                    name=ward_name,
                    constituency=constituency,
                    defaults={'code': f"{constituency.code}{j:02d}"}
                )
                
                # Create 1 polling center per ward
                center_name = f"{ward.name} Polling Center"
                center, _ = PollingCenter.objects.get_or_create(
                    name=center_name,
                    ward=ward,
                    defaults={'code': f"{ward.code}01"}
                )
                
                # Create 2 polling stations per center
                for k in range(1, 3):
                    station_name = f"{center_name} Station {k}"
                    PollingStation.objects.get_or_create(
                        name=station_name,
                        center=center,
                        defaults={'code': f"{center.code}{k:02d}"}
                    )

    def create_basic_candidates(self):
        parties = list(Party.objects.all())
        
        # Presidential candidates
        president_pos = Position.objects.get(name='PRESIDENT')
        presidential_candidates = [
            ('William', 'Ruto', parties[2]),
            ('Raila', 'Odinga', parties[1]),
            ('Kalonzo', 'Musyoka', parties[3]),
        ]
        
        for first_name, last_name, party in presidential_candidates:
            Candidate.objects.get_or_create(
                id_number=f"PRES{first_name[:3].upper()}{random.randint(100, 999)}",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'party': party,
                    'position': president_pos,
                }
            )
        
        # Governor candidates for each county
        governor_pos = Position.objects.get(name='GOVERNOR')
        for county in County.objects.all():
            for i in range(2):
                first_name = f"Governor{i+1}_{county.name[:3]}"
                last_name = f"Candidate{i+1}"
                party = parties[i % len(parties)]
                Candidate.objects.get_or_create(
                    id_number=f"GOV{county.code}{i+1}{random.randint(10, 99)}",
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'party': party,
                        'position': governor_pos,
                        'county': county,
                    }
                )
        
        # MP candidates for each constituency
        mp_pos = Position.objects.get(name='MP')
        for constituency in Constituency.objects.all():
            for i in range(3):
                first_name = f"MP{i+1}_{constituency.name[:3]}"
                last_name = f"Candidate{i+1}"
                party = parties[i % len(parties)]
                Candidate.objects.get_or_create(
                    id_number=f"MP{constituency.code}{i+1}{random.randint(10, 99)}",
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'party': party,
                        'position': mp_pos,
                        'county': constituency.county,
                        'constituency': constituency,
                    }
                )
        
        # MCA candidates for each ward
        mca_pos = Position.objects.get(name='MCA')
        for ward in Ward.objects.all():
            for i in range(2):
                first_name = f"MCA{i+1}_{ward.name[:3]}"
                last_name = f"Candidate{i+1}"
                party = parties[i % len(parties)]
                Candidate.objects.get_or_create(
                    id_number=f"MCA{ward.code}{i+1}{random.randint(10, 99)}",
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'party': party,
                        'position': mca_pos,
                        'county': ward.constituency.county,
                        'constituency': ward.constituency,
                        'ward': ward,
                    }
                )
        
        self.stdout.write('Created basic candidates')
