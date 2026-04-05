#!/usr/bin/env python
from voting.models import County, Constituency, Ward, Position, Candidate, Party
import os
import sys
import django

# Add the elections directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()


def import_mca_candidates():
    """Import MCA candidates from the complete CSV data"""

    mca_position = Position.objects.get(name='MCA')

    # Sample of the complete CSV data - starting with Mombasa
    csv_data = [
        ('001', 'Mombasa', '001', 'Changamwe', '0001', 'Port Reitz',
         'Member of County Assembly', '1', 'Veronica Wanjala', 'DAP-K'),
        ('001', 'Mombasa', '001', 'Changamwe', '0001', 'Port Reitz',
         'Member of County Assembly', '2', 'Stella Kibet', 'ODM'),
        ('001', 'Mombasa', '001', 'Changamwe', '0002', 'Kipevu',
         'Member of County Assembly', '1', 'Kevin Otieno', 'UDA'),
        ('001', 'Mombasa', '001', 'Changamwe', '0002', 'Kipevu',
         'Member of County Assembly', '2', 'Caroline Barasa', 'WIPER'),
        ('001', 'Mombasa', '001', 'Changamwe', '0003', 'Airport',
         'Member of County Assembly', '1', 'Lucy Wamalwa', 'WIPER'),
        ('001', 'Mombasa', '001', 'Changamwe', '0003', 'Airport',
         'Member of County Assembly', '2', 'Dennis Njoroge', 'JUBILEE'),
        ('001', 'Mombasa', '001', 'Changamwe', '0004', 'Changamwe',
         'Member of County Assembly', '1', 'Victor Ndungu', 'ODM'),
        ('001', 'Mombasa', '001', 'Changamwe', '0004', 'Changamwe',
         'Member of County Assembly', '2', 'Agnes Njoroge', 'JUBILEE'),
        ('001', 'Mombasa', '001', 'Changamwe', '0005', 'Chaani',
         'Member of County Assembly', '1', 'Veronica Maina', 'KANU'),
        ('001', 'Mombasa', '001', 'Changamwe', '0005', 'Chaani',
         'Member of County Assembly', '2', 'Paul Cheruiyot', 'UDA'),
        ('001', 'Mombasa', '002', 'Jomvu', '0006', 'Jomvu Kuu',
         'Member of County Assembly', '1', 'Grace Mwangi', 'DAP-K'),
        ('001', 'Mombasa', '002', 'Jomvu', '0006', 'Jomvu Kuu',
         'Member of County Assembly', '2', 'Stephen Wamalwa', 'PNU'),
        ('001', 'Mombasa', '002', 'Jomvu', '0007', 'Miritini',
         'Member of County Assembly', '1', 'Faith Omondi', 'KANU'),
        ('001', 'Mombasa', '002', 'Jomvu', '0007', 'Miritini',
         'Member of County Assembly', '2', 'Mary Otieno', 'WIPER'),
        ('001', 'Mombasa', '002', 'Jomvu', '0008', 'Mikindani',
         'Member of County Assembly', '1', 'Victor Wamalwa', 'DAP-K'),
        ('001', 'Mombasa', '002', 'Jomvu', '0008', 'Mikindani',
         'Member of County Assembly', '2', 'Lucy Njoroge', 'PNU'),
        ('001', 'Mombasa', '003', 'Kisauni', '0009', 'Mjambere',
         'Member of County Assembly', '1', 'John Kiprotich', 'WIPER'),
        ('001', 'Mombasa', '003', 'Kisauni', '0009', 'Mjambere',
         'Member of County Assembly', '2', 'Samuel Odhiambo', 'INDEPENDENT'),
        ('001', 'Mombasa', '003', 'Kisauni', '0010', 'Junda',
         'Member of County Assembly', '1', 'Kevin Ndungu', 'KANU'),
        ('001', 'Mombasa', '003', 'Kisauni', '0010', 'Junda',
         'Member of County Assembly', '2', 'Anthony Kiptoo', 'WIPER'),
        ('001', 'Mombasa', '003', 'Kisauni', '0011', 'Bamburi',
         'Member of County Assembly', '1', 'Anthony Ochieng', 'UDA'),
        ('001', 'Mombasa', '003', 'Kisauni', '0011', 'Bamburi',
         'Member of County Assembly', '2', 'Mark Wanjala', 'DAP-K'),
        ('001', 'Mombasa', '003', 'Kisauni', '0012', 'Mwakirunge',
         'Member of County Assembly', '1', 'Dennis Wamalwa', 'WIPER'),
        ('001', 'Mombasa', '003', 'Kisauni', '0012', 'Mwakirunge',
         'Member of County Assembly', '2', 'Lucy Nyong\'o', 'KANU'),
        ('001', 'Mombasa', '003', 'Kisauni', '0013', 'Mtopanga',
         'Member of County Assembly', '1', 'Mary Barasa', 'UDA'),
        ('001', 'Mombasa', '003', 'Kisauni', '0013', 'Mtopanga',
         'Member of County Assembly', '2', 'Hellen Maina', 'PNU'),
        ('001', 'Mombasa', '003', 'Kisauni', '0014', 'Magogoni',
         'Member of County Assembly', '1', 'Ruth Maina', 'INDEPENDENT'),
        ('001', 'Mombasa', '003', 'Kisauni', '0014', 'Magogoni',
         'Member of County Assembly', '2', 'David Wanjala', 'ODM'),
        ('001', 'Mombasa', '003', 'Kisauni', '0015', 'Shanzu',
         'Member of County Assembly', '1', 'Faith Mutua', 'JUBILEE'),
        ('001', 'Mombasa', '003', 'Kisauni', '0015', 'Shanzu',
         'Member of County Assembly', '2', 'Mark Kiprotich', 'WIPER'),
        ('001', 'Mombasa', '004', 'Nyali', '0016', 'Frere Town',
         'Member of County Assembly', '1', 'Hellen Wanjala', 'ODM'),
        ('001', 'Mombasa', '004', 'Nyali', '0016', 'Frere Town',
         'Member of County Assembly', '2', 'Andrew Cheruiyot', 'WIPER'),
        ('001', 'Mombasa', '004', 'Nyali', '0017', 'Ziwa La Ng\'ombe',
         'Member of County Assembly', '1', 'Joyce Kibet', 'KANU'),
        ('001', 'Mombasa', '004', 'Nyali', '0017', 'Ziwa La Ng\'ombe',
         'Member of County Assembly', '2', 'Veronica Mwangi', 'JUBILEE'),
        ('001', 'Mombasa', '004', 'Nyali', '0018', 'Mkomani',
         'Member of County Assembly', '1', 'Michael Nyong\'o', 'INDEPENDENT'),
        ('001', 'Mombasa', '004', 'Nyali', '0018', 'Mkomani',
         'Member of County Assembly', '2', 'Phoebe Maina', 'UDA'),
        ('001', 'Mombasa', '004', 'Nyali', '0019', 'Kongowea',
         'Member of County Assembly', '1', 'Veronica Mutua', 'PNU'),
        ('001', 'Mombasa', '004', 'Nyali', '0019', 'Kongowea',
         'Member of County Assembly', '2', 'Mark Mwangi', 'INDEPENDENT'),
        ('001', 'Mombasa', '004', 'Nyali', '0020', 'Kadzandani',
         'Member of County Assembly', '1', 'Martin Kariuki', 'PNU'),
        ('001', 'Mombasa', '004', 'Nyali', '0020', 'Kadzandani',
         'Member of County Assembly', '2', 'Ruth Kamau', 'ODM'),
        ('001', 'Mombasa', '005', 'Likoni', '0021', 'Mtongwe',
         'Member of County Assembly', '1', 'Anthony Kiprotich', 'WIPER'),
        ('001', 'Mombasa', '005', 'Likoni', '0021', 'Mtongwe',
         'Member of County Assembly', '2', 'Jane Odhiambo', 'KANU'),
        ('001', 'Mombasa', '005', 'Likoni', '0022', 'Shika Adabu',
         'Member of County Assembly', '1', 'Stella Munyua', 'PNU'),
        ('001', 'Mombasa', '005', 'Likoni', '0022', 'Shika Adabu',
         'Member of County Assembly', '2', 'Joyce Omondi', 'WIPER'),
        ('001', 'Mombasa', '005', 'Likoni', '0023', 'Bofu',
         'Member of County Assembly', '1', 'Mary Maina', 'WIPER'),
        ('001', 'Mombasa', '005', 'Likoni', '0023', 'Bofu',
         'Member of County Assembly', '2', 'Esther Munyua', 'KANU'),
        ('001', 'Mombasa', '005', 'Likoni', '0024', 'Likoni',
         'Member of County Assembly', '1', 'Victor Kiprotich', 'DAP-K'),
        ('001', 'Mombasa', '005', 'Likoni', '0024', 'Likoni',
         'Member of County Assembly', '2', 'Joyce Kiprotich', 'PNU'),
        ('001', 'Mombasa', '005', 'Likoni', '0025', 'Timbwani',
         'Member of County Assembly', '1', 'Esther Munyua', 'INDEPENDENT'),
        ('001', 'Mombasa', '005', 'Likoni', '0025', 'Timbwani',
         'Member of County Assembly', '2', 'Jane Kamau', 'UDA'),
        ('001', 'Mombasa', '006', 'Mvita', '0026', 'Mji Wa Kale/Makadara',
         'Member of County Assembly', '1', 'Caroline Ochieng', 'DAP-K'),
        ('001', 'Mombasa', '006', 'Mvita', '0026', 'Mji Wa Kale/Makadara',
         'Member of County Assembly', '2', 'Mary Cheruiyot', 'ODM'),
        ('001', 'Mombasa', '006', 'Mvita', '0027', 'Tudor',
         'Member of County Assembly', '1', 'Mary Barasa', 'JUBILEE'),
        ('001', 'Mombasa', '006', 'Mvita', '0027', 'Tudor',
         'Member of County Assembly', '2', 'Diana Wanjala', 'DAP-K'),
        ('001', 'Mombasa', '006', 'Mvita', '0028', 'Tononoka',
         'Member of County Assembly', '1', 'Daniel Njoroge', 'UDA'),
        ('001', 'Mombasa', '006', 'Mvita', '0028', 'Tononoka',
         'Member of County Assembly', '2', 'Irene Barasa', 'DAP-K'),
        ('001', 'Mombasa', '006', 'Mvita', '0029', 'Shimanzi/Ganjoni',
         'Member of County Assembly', '1', 'Brian Nyong\'o', 'DAP-K'),
        ('001', 'Mombasa', '006', 'Mvita', '0029', 'Shimanzi/Ganjoni',
         'Member of County Assembly', '2', 'Mark Wamalwa', 'WIPER'),
        ('001', 'Mombasa', '006', 'Mvita', '0030', 'Majengo',
         'Member of County Assembly', '1', 'Hellen Wamalwa', 'INDEPENDENT'),
        ('001', 'Mombasa', '006', 'Mvita', '0030', 'Majengo',
         'Member of County Assembly', '2', 'Stella Kiptoo', 'UDA'),
        # Kwale County
        ('002', 'Kwale', '007', 'Msambweni', '0031', 'Gombato Bongwe',
         'Member of County Assembly', '1', 'Joseph Maina', 'UDA'),
        ('002', 'Kwale', '007', 'Msambweni', '0031', 'Gombato Bongwe',
         'Member of County Assembly', '2', 'Esther Kamau', 'DAP-K'),
        ('002', 'Kwale', '007', 'Msambweni', '0032', 'Ukunda',
         'Member of County Assembly', '1', 'Esther Kariuki', 'DAP-K'),
        ('002', 'Kwale', '007', 'Msambweni', '0032', 'Ukunda',
         'Member of County Assembly', '2', 'Grace Mwangi', 'ODM'),
        ('002', 'Kwale', '007', 'Msambweni', '0033', 'Kinondo',
         'Member of County Assembly', '1', 'Ruth Kariuki', 'WIPER'),
        ('002', 'Kwale', '007', 'Msambweni', '0033', 'Kinondo',
         'Member of County Assembly', '2', 'Lucy Munyua', 'PNU'),
        ('002', 'Kwale', '007', 'Msambweni', '0034', 'Ramisi',
         'Member of County Assembly', '1', 'John Cheruiyot', 'INDEPENDENT'),
        ('002', 'Kwale', '007', 'Msambweni', '0034', 'Ramisi',
         'Member of County Assembly', '2', 'Grace Wanjala', 'UDA'),
        ('002', 'Kwale', '008', 'Lungalunga', '0035', 'Pongwe/Kikoneni',
         'Member of County Assembly', '1', 'George Munyua', 'DAP-K'),
        ('002', 'Kwale', '008', 'Lungalunga', '0035', 'Pongwe/Kikoneni',
         'Member of County Assembly', '2', 'Michael Otieno', 'WIPER'),
        ('002', 'Kwale', '008', 'Lungalunga', '0036', 'Dzombo',
         'Member of County Assembly', '1', 'Dennis Barasa', 'ODM'),
        ('002', 'Kwale', '008', 'Lungalunga', '0036', 'Dzombo',
         'Member of County Assembly', '2', 'Joseph Wanjala', 'UDA'),
        ('002', 'Kwale', '008', 'Lungalunga', '0037', 'Mwereni',
         'Member of County Assembly', '1', 'Mary Kibet', 'KANU'),
        ('002', 'Kwale', '008', 'Lungalunga', '0037', 'Mwereni',
         'Member of County Assembly', '2', 'Hellen Mwangi', 'DAP-K'),
        ('002', 'Kwale', '008', 'Lungalunga', '0038', 'Vanga',
         'Member of County Assembly', '1', 'Lydia Cheruiyot', 'JUBILEE'),
        ('002', 'Kwale', '008', 'Lungalunga', '0038', 'Vanga',
         'Member of County Assembly', '2', 'George Kiprotich', 'KANU'),
        ('002', 'Kwale', '009', 'Matuga', '0039', 'Tsimba Golini',
         'Member of County Assembly', '1', 'Joseph Odhiambo', 'ODM'),
        ('002', 'Kwale', '009', 'Matuga', '0039', 'Tsimba Golini',
         'Member of County Assembly', '2', 'Kevin Omondi', 'KANU'),
        ('002', 'Kwale', '009', 'Matuga', '0040', 'Waa',
         'Member of County Assembly', '1', 'Brian Njoroge', 'KANU'),
        ('002', 'Kwale', '009', 'Matuga', '0040', 'Waa',
         'Member of County Assembly', '2', 'Brian Mutua', 'PNU'),
        ('002', 'Kwale', '009', 'Matuga', '0041', 'Tiwi',
         'Member of County Assembly', '1', 'Agnes Ochieng', 'DAP-K'),
        ('002', 'Kwale', '009', 'Matuga', '0041', 'Tiwi',
         'Member of County Assembly', '2', 'David Mutua', 'WIPER'),
        ('002', 'Kwale', '009', 'Matuga', '0042', 'Kubo South',
         'Member of County Assembly', '1', 'Irene Kiptoo', 'INDEPENDENT'),
        ('002', 'Kwale', '009', 'Matuga', '0042', 'Kubo South',
         'Member of County Assembly', '2', 'Stephen Wamalwa', 'PNU'),
        ('002', 'Kwale', '009', 'Matuga', '0043', 'Mkongani',
         'Member of County Assembly', '1', 'Benard Omondi', 'UDA'),
        ('002', 'Kwale', '009', 'Matuga', '0043', 'Mkongani',
         'Member of County Assembly', '2', 'Susan Munyua', 'JUBILEE'),
        ('002', 'Kwale', '010', 'Kinango', '0044', 'Ndavaya',
         'Member of County Assembly', '1', 'Joyce Barasa', 'INDEPENDENT'),
        ('002', 'Kwale', '010', 'Kinango', '0044', 'Ndavaya',
         'Member of County Assembly', '2', 'Diana Mutua', 'ODM'),
        ('002', 'Kwale', '010', 'Kinango', '0045', 'Puma',
         'Member of County Assembly', '1', 'Peter Barasa', 'JUBILEE'),
        ('002', 'Kwale', '010', 'Kinango', '0045', 'Puma',
         'Member of County Assembly', '2', 'George Cheruiyot', 'INDEPENDENT'),
        ('002', 'Kwale', '010', 'Kinango', '0046', 'Kinango',
         'Member of County Assembly', '1', 'Irene Kariuki', 'ODM'),
        ('002', 'Kwale', '010', 'Kinango', '0046', 'Kinango',
         'Member of County Assembly', '2', 'Beatrice Ochieng', 'KANU'),
        ('002', 'Kwale', '010', 'Kinango', '0047', 'Mackinnon Road',
         'Member of County Assembly', '1', 'Andrew Kiprotich', 'WIPER'),
        ('002', 'Kwale', '010', 'Kinango', '0047', 'Mackinnon Road',
         'Member of County Assembly', '2', 'Andrew Otieno', 'JUBILEE'),
        ('002', 'Kwale', '010', 'Kinango', '0048', 'Chengoni/Samburu',
         'Member of County Assembly', '1', 'Victor Mutua', 'UDA'),
        ('002', 'Kwale', '010', 'Kinango', '0048', 'Chengoni/Samburu',
         'Member of County Assembly', '2', 'Ruth Ndungu', 'JUBILEE'),
        ('002', 'Kwale', '010', 'Kinango', '0049', 'Mwavumbo',
         'Member of County Assembly', '1', 'Stella Ochieng', 'KANU'),
        ('002', 'Kwale', '010', 'Kinango', '0049', 'Mwavumbo',
         'Member of County Assembly', '2', 'Susan Wamalwa', 'WIPER'),
        ('002', 'Kwale', '010', 'Kinango', '0050', 'Kasemeni',
         'Member of County Assembly', '1', 'Joseph Wamalwa', 'KANU'),
        ('002', 'Kwale', '010', 'Kinango', '0050', 'Kasemeni',
         'Member of County Assembly', '2', 'Anthony Wamalwa', 'ODM'),
    ]

    imported_count = 0
    error_count = 0

    for row in csv_data:
        county_code, county_name, constituency_code, constituency_name, ward_code, ward_name, position, candidate_no, candidate_name, party = row

        try:
            # Get county
            county = County.objects.get(name=county_name)

            # Get constituency
            constituency = county.constituency_set.filter(
                name__icontains=constituency_name).first()
            if not constituency:
                constituency = county.constituency_set.first()

            # Get or create ward
            ward, created = Ward.objects.get_or_create(
                name=ward_name,
                constituency=constituency,
                defaults={'code': ward_code}
            )

            # Get or create party
            party_obj, created = Party.objects.get_or_create(name=party)

            # Create candidate
            name_parts = candidate_name.split()
            candidate = Candidate.objects.create(
                first_name=name_parts[0],
                last_name=' '.join(name_parts[1:]) if len(
                    name_parts) > 1 else '',
                county=county,
                constituency=constituency,
                ward=ward,
                position=mca_position,
                party=party_obj,
                id_number=f'MCA{ward_code}{candidate_no}'
            )

            imported_count += 1
            print(
                f'Imported: {candidate_name} - {party} ({ward_name}, {county_name})')

        except Exception as e:
            error_count += 1
            print(f'Error importing {candidate_name}: {e}')

    print(f'\n=== IMPORT SUMMARY ===')
    print(f'Successfully imported: {imported_count} candidates')
    print(f'Errors encountered: {error_count}')

    # Get final counts
    total_mcas = Candidate.objects.filter(position=mca_position).count()
    print(f'Total MCA candidates in database: {total_mcas}')


if __name__ == '__main__':
    import_mca_candidates()
