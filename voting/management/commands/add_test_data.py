from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward, PollingCenter, PollingStation, Position, Party, Candidate
import random

class Command(BaseCommand):
    help = 'Add basic test data for registration'

    def handle(self, *args, **options):
        self.stdout.write('Adding basic test data...')
        
        # Create parties
        parties = [
            ('Jubilee Party', 'JP'),
            ('ODM', 'Orange Democratic Movement'),
            ('UDA', 'United Democratic Alliance'),
        ]
        
        for name, desc in parties:
            Party.objects.get_or_create(name=name, defaults={'description': desc})
        
        # Create positions
        positions = [
            ('PRESIDENT', 'President of the Republic of Kenya'),
            ('GOVERNOR', 'County Governor'),
            ('MP', 'Member of Parliament'),
            ('MCA', 'Member of County Assembly'),
        ]
        
        for name, desc in positions:
            Position.objects.get_or_create(name=name, defaults={'description': desc})
        
        # Get existing Mombasa county and add more
        if County.objects.count() == 1:
            mombasa = County.objects.first()
            
            # Add constituencies for Mombasa
            for i in range(1, 4):
                constituency = Constituency.objects.get_or_create(
                    name=f"Mombasa Constituency {i}",
                    county=mombasa,
                    defaults={'code': f"001{i:02d}"}
                )[0]
                
                # Add wards for each constituency
                for j in range(1, 3):
                    ward = Ward.objects.get_or_create(
                        name=f"Mombasa Constituency {i} Ward {j}",
                        constituency=constituency,
                        defaults={'code': f"001{i:02d}{j:02d}"}
                    )[0]
                    
                    # Add polling center for each ward
                    center = PollingCenter.objects.get_or_create(
                        name=f"Mombasa Constituency {i} Ward {j} Center",
                        ward=ward,
                        defaults={'code': f"001{i:02d}{j:02d}01"}
                    )[0]
                    
                    # Add polling stations for each center
                    for k in range(1, 3):
                        PollingStation.objects.get_or_create(
                            name=f"Mombasa Constituency {i} Ward {j} Station {k}",
                            center=center,
                            defaults={'code': f"001{i:02d}{j:02d}01{k:02d}"}
                        )
        
        # Add some more counties
        counties_to_add = [
            ('Nairobi', '002'),
            ('Kisumu', '003'),
            ('Nakuru', '004'),
        ]
        
        for name, code in counties_to_add:
            county = County.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )[0]
            
            # Add basic structure for each county
            for i in range(1, 3):
                constituency = Constituency.objects.get_or_create(
                    name=f"{name} Constituency {i}",
                    county=county,
                    defaults={'code': f"{code}{i:02d}"}
                )[0]
                
                ward = Ward.objects.get_or_create(
                    name=f"{name} Constituency {i} Ward 1",
                    constituency=constituency,
                    defaults={'code': f"{code}{i:02d}01"}
                )[0]
                
                center = PollingCenter.objects.get_or_create(
                    name=f"{name} Constituency {i} Ward 1 Center",
                    ward=ward,
                    defaults={'code': f"{code}{i:02d}0101"}
                )[0]
                
                PollingStation.objects.get_or_create(
                    name=f"{name} Constituency {i} Ward 1 Station 1",
                    center=center,
                    defaults={'code': f"{code}{i:02d}010101"}
                )
        
        # Add some candidates
        party_list = list(Party.objects.all())
        president_pos = Position.objects.get(name='PRESIDENT')
        
        # Presidential candidates
        candidates = [
            ('William', 'Ruto', party_list[2] if len(party_list) > 2 else party_list[0]),
            ('Raila', 'Odinga', party_list[1] if len(party_list) > 1 else party_list[0]),
            ('Kalonzo', 'Musyoka', party_list[0]),
        ]
        
        for first, last, party in candidates:
            Candidate.objects.get_or_create(
                id_number=f"PRES{first[:3].upper()}{random.randint(100, 999)}",
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'party': party,
                    'position': president_pos,
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Basic test data added successfully!'))
