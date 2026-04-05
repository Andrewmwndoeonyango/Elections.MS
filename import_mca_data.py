#!/usr/bin/env python
"""
Import MCA candidates from CSV data
This script imports Member of County Assembly candidates for all wards
"""

from voting.models import County, Constituency, Ward, Position, Candidate, Party
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()


def clear_existing_mca_candidates():
    """Clear existing MCA candidates"""
    mca_position = Position.objects.get(name='MCA')
    existing_mcas = Candidate.objects.filter(position=mca_position)
    count = existing_mcas.count()
    existing_mcas.delete()
    print(f"Cleared {count} existing MCA candidates")


def import_mca_candidates():
    """Import MCA candidates from the provided data"""
    mca_position = Position.objects.get(name='MCA')

    # County name mapping from CSV to database
    county_mapping = {
        'MOMBASA': 'Mombasa',
        'KWALE': 'Kwale',
        'KILIFI': 'Kilifi',
        'TANA RIVER': 'Tana River',
        'LAMU': 'Lamu',
        'TAITA TAVETA': 'Taita Taveta',
        'GARISSA': 'Garissa',
        'WAJIR': 'Wajir',
        'MANDERA': 'Mandera',
        'MARSABIT': 'Marsabit',
        'ISIOLO': 'Isiolo',
        'MERU': 'Meru',
        'THARAKA NITHI': 'Tharaka Nithi',
        'EMBU': 'Embu',
        'KITUI': 'Kitui',
        'MACHAKOS': 'Machakos',
        'MAKUENI': 'Makueni',
        'NYANDARUA': 'Nyandarua',
        'NYERI': 'Nyeri',
        'KIRINYAGA': 'Kirinyaga',
        'MURANGA': 'Muranga',
        'KIAMBU': 'Kiambu',
        'TURKANA': 'Turkana',
        'WEST POKOT': 'West Pokot',
        'SAMBURU': 'Samburu',
        'TRANS NZOIA': 'Trans Nzoia',
        'UASIN GISHU': 'Uasin Gishu',
        'ELGEYO MARAKWET': 'Elgeyo Marakwet',
        'NANDI': 'Nandi',
        'BARINGO': 'Baringo',
        'LAIKIPIA': 'Laikipia',
        'NAKURU': 'Nakuru',
        'NAROK': 'Narok',
        'KAJIADO': 'Kajiado',
        'KERICHO': 'Kericho',
        'BOMET': 'Bomet',
        'KAKAMEGA': 'Kakamega',
        'VIHIGA': 'Vihiga',
        'BUNGOMA': 'Bungoma',
        'BUSIA': 'Busia',
        'SIAYA': 'Siaya',
        'KISUMU': 'Kisumu',
        'HOMA BAY': 'Homa Bay',
        'MIGORI': 'Migori',
        'KISII': 'Kisii',
        'NYAMIRA': 'Nyamira',
        'NAIROBI CITY': 'Nairobi'
    }

    # MCA candidate data from CSV (first batch)
    mca_data = [
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0001', 'PORT REITZ',
         'Member of County Assembly', '1', 'Veronica Wanjala', 'DAP-K'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0001', 'PORT REITZ',
         'Member of County Assembly', '2', 'Stella Kibet', 'ODM'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0002', 'KIPEVU',
         'Member of County Assembly', '1', 'Kevin Otieno', 'UDA'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0002', 'KIPEVU',
         'Member of County Assembly', '2', 'Caroline Barasa', 'WIPER'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0003', 'AIRPORT',
         'Member of County Assembly', '1', 'Lucy Wamalwa', 'WIPER'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0003', 'AIRPORT',
         'Member of County Assembly', '2', 'Dennis Njoroge', 'JUBILEE'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0004', 'CHANGAMWE',
         'Member of County Assembly', '1', 'Victor Ndungu', 'ODM'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0004', 'CHANGAMWE',
         'Member of County Assembly', '2', 'Agnes Njoroge', 'JUBILEE'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0005', 'CHAANI',
         'Member of County Assembly', '1', 'Veronica Maina', 'KANU'),
        ('001', 'MOMBASA', '001', 'CHANGAMWE', '0005', 'CHAANI',
         'Member of County Assembly', '2', 'Paul Cheruiyot', 'UDA'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0006', 'JOMVU KUU',
         'Member of County Assembly', '1', 'Grace Mwangi', 'DAP-K'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0006', 'JOMVU KUU',
         'Member of County Assembly', '2', 'Stephen Wamalwa', 'PNU'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0007', 'MIRITINI',
         'Member of County Assembly', '1', 'Faith Omondi', 'KANU'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0007', 'MIRITINI',
         'Member of County Assembly', '2', 'Mary Otieno', 'WIPER'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0008', 'MIKINDANI',
         'Member of County Assembly', '1', 'Victor Wamalwa', 'DAP-K'),
        ('001', 'MOMBASA', '002', 'JOMVU', '0008', 'MIKINDANI',
         'Member of County Assembly', '2', 'Lucy Njoroge', 'PNU'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0009', 'MJAMBERE',
         'Member of County Assembly', '1', 'John Kiprotich', 'WIPER'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0009', 'MJAMBERE',
         'Member of County Assembly', '2', 'Samuel Odhiambo', 'INDEPENDENT'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0010', 'JUNDA',
         'Member of County Assembly', '1', 'Kevin Ndungu', 'KANU'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0010', 'JUNDA',
         'Member of County Assembly', '2', 'Anthony Kiptoo', 'WIPER'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0011', 'BAMBURI',
         'Member of County Assembly', '1', 'Anthony Ochieng', 'UDA'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0011', 'BAMBURI',
         'Member of County Assembly', '2', 'Mark Wanjala', 'DAP-K'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0012', 'MWAKIRUNGE',
         'Member of County Assembly', '1', 'Dennis Wamalwa', 'WIPER'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0012', 'MWAKIRUNGE',
         'Member of County Assembly', '2', 'Lucy Nyong\'o', 'KANU'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0013', 'MTOPANGA',
         'Member of County Assembly', '1', 'Mary Barasa', 'UDA'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0013', 'MTOPANGA',
         'Member of County Assembly', '2', 'Hellen Maina', 'PNU'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0014', 'MAGOGONI',
         'Member of County Assembly', '1', 'Ruth Maina', 'INDEPENDENT'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0014', 'MAGOGONI',
         'Member of County Assembly', '2', 'David Wanjala', 'ODM'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0015', 'SHANZU',
         'Member of County Assembly', '1', 'Faith Mutua', 'JUBILEE'),
        ('001', 'MOMBASA', '003', 'KISAUNI', '0015', 'SHANZU',
         'Member of County Assembly', '2', 'Mark Kiprotich', 'WIPER'),
        ('001', 'MOMBASA', '004', 'NYALI', '0016', 'FRERE TOWN',
         'Member of County Assembly', '1', 'Hellen Wanjala', 'ODM'),
        ('001', 'MOMBASA', '004', 'NYALI', '0016', 'FRERE TOWN',
         'Member of County Assembly', '2', 'Andrew Cheruiyot', 'WIPER'),
        ('001', 'MOMBASA', '004', 'NYALI', '0017', 'ZIWA LA NG\'OMBE',
         'Member of County Assembly', '1', 'Joyce Kibet', 'KANU'),
        ('001', 'MOMBASA', '004', 'NYALI', '0017', 'ZIWA LA NG\'OMBE',
         'Member of County Assembly', '2', 'Veronica Mwangi', 'JUBILEE'),
        ('001', 'MOMBASA', '004', 'NYALI', '0018', 'MKOMANI',
         'Member of County Assembly', '1', 'Michael Nyong\'o', 'INDEPENDENT'),
        ('001', 'MOMBASA', '004', 'NYALI', '0018', 'MKOMANI',
         'Member of County Assembly', '2', 'Phoebe Maina', 'UDA'),
        ('001', 'MOMBASA', '004', 'NYALI', '0019', 'KONGOWEA',
         'Member of County Assembly', '1', 'Veronica Mutua', 'PNU'),
        ('001', 'MOMBASA', '004', 'NYALI', '0019', 'KONGOWEA',
         'Member of County Assembly', '2', 'Mark Mwangi', 'INDEPENDENT'),
        ('001', 'MOMBASA', '004', 'NYALI', '0020', 'KADZANDANI',
         'Member of County Assembly', '1', 'Martin Kariuki', 'PNU'),
        ('001', 'MOMBASA', '004', 'NYALI', '0020', 'KADZANDANI',
         'Member of County Assembly', '2', 'Ruth Kamau', 'ODM'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0021', 'MTONGWE',
         'Member of County Assembly', '1', 'Anthony Kiprotich', 'WIPER'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0021', 'MTONGWE',
         'Member of County Assembly', '2', 'Jane Odhiambo', 'KANU'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0022', 'SHIKA ADABU',
         'Member of County Assembly', '1', 'Stella Munyua', 'PNU'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0022', 'SHIKA ADABU',
         'Member of County Assembly', '2', 'Joyce Omondi', 'WIPER'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0023', 'BOFU',
         'Member of County Assembly', '1', 'Mary Maina', 'WIPER'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0023', 'BOFU',
         'Member of County Assembly', '2', 'Esther Munyua', 'KANU'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0024', 'LIKONI',
         'Member of County Assembly', '1', 'Victor Kiprotich', 'DAP-K'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0024', 'LIKONI',
         'Member of County Assembly', '2', 'Joyce Kiprotich', 'PNU'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0025', 'TIMBWANI',
         'Member of County Assembly', '1', 'Esther Munyua', 'INDEPENDENT'),
        ('001', 'MOMBASA', '005', 'LIKONI', '0025', 'TIMBWANI',
         'Member of County Assembly', '2', 'Jane Kamau', 'UDA'),
        ('001', 'MOMBASA', '006', 'MVITA', '0026', 'MJI WA KALE/MAKADARA',
         'Member of County Assembly', '1', 'Caroline Ochieng', 'DAP-K'),
        ('001', 'MOMBASA', '006', 'MVITA', '0026', 'MJI WA KALE/MAKADARA',
         'Member of County Assembly', '2', 'Mary Cheruiyot', 'ODM'),
        ('001', 'MOMBASA', '006', 'MVITA', '0027', 'TUDOR',
         'Member of County Assembly', '1', 'Mary Barasa', 'JUBILEE'),
        ('001', 'MOMBASA', '006', 'MVITA', '0027', 'TUDOR',
         'Member of County Assembly', '2', 'Diana Wanjala', 'DAP-K'),
        ('001', 'MOMBASA', '006', 'MVITA', '0028', 'TONONOKA',
         'Member of County Assembly', '1', 'Daniel Njoroge', 'UDA'),
        ('001', 'MOMBASA', '006', 'MVITA', '0028', 'TONONOKA',
         'Member of County Assembly', '2', 'Irene Barasa', 'DAP-K'),
        ('001', 'MOMBASA', '006', 'MVITA', '0029', 'SHIMANZI/GANJONI',
         'Member of County Assembly', '1', 'Brian Nyong\'o', 'DAP-K'),
        ('001', 'MOMBASA', '006', 'MVITA', '0029', 'SHIMANZI/GANJONI',
         'Member of County Assembly', '2', 'Mark Wamalwa', 'WIPER'),
        ('001', 'MOMBASA', '006', 'MVITA', '0030', 'MAJENGO',
         'Member of County Assembly', '1', 'Hellen Wamalwa', 'INDEPENDENT'),
        ('001', 'MOMBASA', '006', 'MVITA', '0030', 'MAJENGO',
         'Member of County Assembly', '2', 'Stella Kiptoo', 'UDA'),
    ]

    imported_count = 0
    error_count = 0

    for row in mca_data:
        county_code, county_name, constituency_code, constituency_name, ward_code, ward_name, position, candidate_no, candidate_name, party = row

        try:
            # Get county using mapping
            db_county_name = county_mapping.get(county_name, county_name)
            county = County.objects.get(name=db_county_name)

            # Get constituency (try to find by name)
            constituency = county.constituency_set.filter(
                name__icontains=constituency_name).first()
            if not constituency:
                # If not found, use first constituency in county
                constituency = county.constituency_set.first()
                if not constituency:
                    print(f"No constituency found for {county_name}")
                    continue

            # Get or create ward
            ward, created = Ward.objects.get_or_create(
                name=ward_name,
                constituency=constituency,
                defaults={'code': ward_code}
            )

            # Get or create party
            party, created = Party.objects.get_or_create(name=party)

            # Split candidate name
            name_parts = candidate_name.split()
            first_name = name_parts[0]
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

            # Create candidate
            candidate = Candidate.objects.create(
                first_name=first_name,
                last_name=last_name,
                county=county,
                constituency=constituency,
                ward=ward,
                position=mca_position,
                party=party,
                id_number=f'MCA{ward_code[:4].upper()}{candidate_name[:4].upper()}'
            )

            imported_count += 1
            print(
                f'Imported: {candidate_name} - {party} ({ward_name}, {constituency_name})')

        except Exception as e:
            error_count += 1
            print(f'Error importing {candidate_name}: {e}')

    return imported_count, error_count


def main():
    print("=== MCA CANDIDATE IMPORT ===")

    # Clear existing MCA candidates
    clear_existing_mca_candidates()

    # Import new MCA candidates
    imported, errors = import_mca_candidates()

    print(f'\n=== IMPORT SUMMARY ===')
    print(f'MCA candidates imported: {imported}')
    print(f'Errors encountered: {errors}')

    # Show final count
    mca_position = Position.objects.get(name='MCA')
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    print(f'Total MCA candidates in database: {total_mcas}')


if __name__ == '__main__':
    main()
