from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward, PollingCenter, PollingStation, Position, Party, Candidate
import random

class Command(BaseCommand):
    help = 'Create functional election data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating functional election data...')
        
        # Create parties
        self.create_parties()
        
        # Create positions
        self.create_positions()
        
        # Create basic counties with working structure
        self.create_working_counties()
        
        # Create candidates
        self.create_candidates()
        
        self.stdout.write(self.style.SUCCESS('Functional election data created!'))

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
        
        self.stdout.write('✅ Created 4 political parties')

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
        
        self.stdout.write('✅ Created 6 election positions')

    def create_working_counties(self):
        # Create 10 major counties with complete working structure
        counties_data = [
            ('Nairobi', '001', 8),   # 8 constituencies
            ('Mombasa', '002', 6),   # 6 constituencies
            ('Kisumu', '003', 7),   # 7 constituencies
            ('Nakuru', '004', 9),   # 9 constituencies
            ('Kiambu', '005', 10),  # 10 constituencies
            ('Turkana', '006', 4),  # 4 constituencies
            ('Kakamega', '007', 10), # 10 constituencies
            ('Bungoma', '008', 7),   # 7 constituencies
            ('Kisii', '009', 7),     # 7 constituencies
            ('Meru', '010', 7),      # 7 constituencies
        ]
        
        for name, code, num_constituencies in counties_data:
            county, created = County.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            
            if created:
                self.create_county_structure(county, num_constituencies)
        
        self.stdout.write(f'✅ Created {County.objects.count()} counties with structure')

    def create_county_structure(self, county, num_constituencies):
        for i in range(1, num_constituencies + 1):
            constituency_name = f"{county.name} Constituency {i}"
            constituency, _ = Constituency.objects.get_or_create(
                name=constituency_name,
                county=county,
                defaults={'code': f"{county.code}{i:02d}"}
            )
            
            # Create 5 wards per constituency
            for j in range(1, 6):
                ward_name = f"{constituency_name} Ward {j}"
                ward, _ = Ward.objects.get_or_create(
                    name=ward_name,
                    constituency=constituency,
                    defaults={'code': f"{constituency.code}{j:02d}"}
                )
                
                # Create 2 polling centers per ward
                for k in range(1, 3):
                    center_name = f"{ward_name} Center {k}"
                    center, _ = PollingCenter.objects.get_or_create(
                        name=center_name,
                        ward=ward,
                        defaults={'code': f"{ward.code}{k:02d}"}
                    )
                    
                    # Create 3 polling stations per center
                    for l in range(1, 4):
                        station_name = f"{center_name} Station {l}"
                        PollingStation.objects.get_or_create(
                            name=station_name,
                            center=center,
                            defaults={'code': f"{center.code}{l:02d}"}
                        )

    def create_candidates(self):
        parties = list(Party.objects.all())
        
        # Presidential candidates (5 candidates)
        self.create_presidential_candidates(parties)
        
        # Governor candidates (2 per county)
        self.create_governor_candidates(parties)
        
        # Senator candidates (2 per county)
        self.create_senator_candidates(parties)
        
        # Women Representative candidates (2 per county)
        self.create_women_rep_candidates(parties)
        
        # MP candidates (3 per constituency)
        self.create_mp_candidates(parties)
        
        # MCA candidates (2 per ward)
        self.create_mca_candidates(parties)

    def create_presidential_candidates(self, parties):
        president_pos = Position.objects.get(name='PRESIDENT')
        
        candidates = [
            ('William', 'Ruto', parties[2]),  # UDA
            ('Raila', 'Odinga', parties[1]),  # ODM
            ('Kalonzo', 'Musyoka', parties[3]), # Wiper
            ('Musalia', 'Mudavadi', parties[0]), # Jubilee
            ('Martha', 'Karua', parties[1]),  # ODM
        ]
        
        for first_name, last_name, party in candidates:
            Candidate.objects.get_or_create(
                id_number=f"PRES{first_name[:3].upper()}{random.randint(100, 999)}",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'party': party,
                    'position': president_pos,
                }
            )
        
        self.stdout.write('✅ Created 5 Presidential candidates')

    def create_governor_candidates(self, parties):
        governor_pos = Position.objects.get(name='GOVERNOR')
        
        for county in County.objects.all():
            # 2 candidates per county with ethnic names
            ethnic_names = self.get_ethnic_names(county.name)
            
            for i, (first_name, last_name) in enumerate(ethnic_names[:2]):
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
        
        self.stdout.write(f'✅ Created Governor candidates (2 per county)')

    def create_senator_candidates(self, parties):
        senator_pos = Position.objects.get(name='SENATOR')
        
        for county in County.objects.all():
            # 2 candidates per county
            ethnic_names = self.get_ethnic_names(county.name)
            
            for i, (first_name, last_name) in enumerate(ethnic_names[:2]):
                party = parties[i % len(parties)]
                Candidate.objects.get_or_create(
                    id_number=f"SEN{county.code}{i+1}{random.randint(10, 99)}",
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'party': party,
                        'position': senator_pos,
                        'county': county,
                    }
                )
        
        self.stdout.write('✅ Created Senator candidates (2 per county)')

    def create_women_rep_candidates(self, parties):
        women_rep_pos = Position.objects.get(name='WOMEN_REP')
        
        for county in County.objects.all():
            # 2 female candidates per county
            female_names = self.get_female_names(county.name)
            
            for i, (first_name, last_name) in enumerate(female_names[:2]):
                party = parties[i % len(parties)]
                Candidate.objects.get_or_create(
                    id_number=f"WR{county.code}{i+1}{random.randint(10, 99)}",
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'party': party,
                        'position': women_rep_pos,
                        'county': county,
                    }
                )
        
        self.stdout.write('✅ Created Women Representative candidates (2 per county)')

    def create_mp_candidates(self, parties):
        mp_pos = Position.objects.get(name='MP')
        
        for constituency in Constituency.objects.all():
            # 3 candidates per constituency
            ethnic_names = self.get_ethnic_names(constituency.county.name)
            
            for i in range(3):
                first_name, last_name = ethnic_names[i % len(ethnic_names)]
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
        
        self.stdout.write(f'✅ Created MP candidates (3 per constituency)')

    def create_mca_candidates(self, parties):
        mca_pos = Position.objects.get(name='MCA')
        
        for ward in Ward.objects.all():
            # 2 candidates per ward
            ethnic_names = self.get_ethnic_names(ward.constituency.county.name)
            
            for i in range(2):
                first_name, last_name = ethnic_names[i % len(ethnic_names)]
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
        
        self.stdout.write(f'✅ Created MCA candidates (2 per ward)')

    def get_ethnic_names(self, county_name):
        # Return ethnically appropriate names for each county
        ethnic_names = {
            'Nairobi': [('Johnson', 'Sakaja'), ('Esther', 'Passaris'), ('Mike', 'Sonko')],
            'Mombasa': [('Ali', 'Hassan'), ('Fatuma', 'Mohamed'), ('Abdullahi', 'Mwarabu')],
            'Kisumu': [('Peter', 'Anyang Nyongo'), ('Ruth', 'Odinga'), ('Grace', 'Onyango')],
            'Nakuru': [('Susan', 'Kihika'), ('Lee', 'Kinyanjui'), ('David', 'Kihara')],
            'Kiambu': [('James', 'Nyoro'), ('Ann', 'Wamuratha'), ('Waititu', 'Kabogo')],
            'Turkana': [('Jeremiah', 'Lomorukai'), ('Elizabeth', 'Loiye'), ('Joseph', 'Ekuwom')],
            'Kakamega': [('Wycliffe', 'Oparanya'), ('Moses', 'Akaranga'), ('Cleophas', 'Malalah')],
            'Bungoma': [('Wycliffe', 'Wamunyinyi'), ('Regina', 'Nyangweso'), ('John', 'Chikati')],
            'Kisii': [('James', 'Ongwae'), ('Dorothy', 'Ochwangi'), ('Simba', 'Arati')],
            'Meru': [('Kiraitu', 'Murungi'), ('Kawira', 'Mwangaza'), ('Mithika', 'Linturi')],
        }
        
        return ethnic_names.get(county_name, [
            ('John', 'Mwangangi'), ('Mary', 'Wanjiru'), ('Peter', 'Kamau')
        ])

    def get_female_names(self, county_name):
        # Return female names for women representatives
        female_names = {
            'Nairobi': [('Esther', 'Passaris'), ('Rachel', 'Shebesh')],
            'Mombasa': [('Aisha', 'Hassan'), ('Fatuma', 'Mohamed')],
            'Kisumu': [('Ruth', 'Odinga'), ('Grace', 'Onyango')],
            'Nakuru': [('Susan', 'Kihika'), ('Martha', 'Mwangi')],
            'Kiambu': [('Ann', 'Wamuratha'), ('Lucy', 'Kariuki')],
            'Turkana': [('Elizabeth', 'Loiye'), ('Naomi', 'Ekal')],
            'Kakamega': [('Mabel', 'Muruli'), ('Lillian', 'Mongare')],
            'Bungoma': [('Regina', 'Nyangweso'), ('Nancy', 'Wabwire')],
            'Kisii': [('Dorothy', 'Ochwangi'), ('Betty', 'Nyaboke')],
            'Meru': [('Kawira', 'Mwangaza'), ('Miriam', 'Kithinji')],
        }
        
        return female_names.get(county_name, [
            ('Mary', 'Wanjiru'), ('Grace', 'Muthoni')
        ])
