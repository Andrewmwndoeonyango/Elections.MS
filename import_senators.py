from voting.models import County, Position, Candidate, Party
import csv
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elections.settings')
django.setup()


def import_senator_candidates():
    """Import senator candidates from CSV data"""

    # Get or create the Senator position
    senator_position, created = Position.objects.get_or_create(
        name='SENATOR',
        defaults={
            'description': 'Senator representing the county at the national level'}
    )

    if created:
        print(f"Created position: {senator_position.name}")
    else:
        print(f"Using existing position: {senator_position.name}")

    # Senator candidates data
    senator_data = [
        ("001", "MOMBASA", "Ruth Otieno", "UDA"),
        ("001", "MOMBASA", "Grace Njoroge", "PNU"),
        ("002", "KWALE", "Joyce Wamalwa", "ODM"),
        ("002", "KWALE", "Diana Kiptoo", "JUBILEE"),
        ("003", "KILIFI", "Daniel Ochieng", "PNU"),
        ("003", "KILIFI", "Mark Otieno", "ODM"),
        ("004", "TANA RIVER", "Andrew Mutua", "ODM"),
        ("004", "TANA RIVER", "Beatrice Ochieng", "PNU"),
        ("005", "LAMU", "Phoebe Kiptoo", "ODM"),
        ("005", "LAMU", "George Wamalwa", "JUBILEE"),
        ("006", "TAITA TAVETA", "Veronica Maina", "ODM"),
        ("006", "TAITA TAVETA", "James Kariuki", "JUBILEE"),
        ("007", "GARISSA", "Paul Kamau", "UDA"),
        ("007", "GARISSA", "Mercy Njoroge", "JUBILEE"),
        ("008", "WAJIR", "Benard Nyong'o", "DAP-K"),
        ("008", "WAJIR", "Victor Kiptoo", "WIPER"),
        ("009", "MANDERA", "Joseph Nyong'o", "ODM"),
        ("009", "MANDERA", "Michael Wamalwa", "JUBILEE"),
        ("010", "MARSABIT", "Diana Ochieng", "KANU"),
        ("010", "MARSABIT", "Mark Kibet", "DAP-K"),
        ("011", "ISIOLO", "Joyce Kamau", "DAP-K"),
        ("011", "ISIOLO", "Veronica Munyua", "PNU"),
        ("012", "MERU", "Victor Kariuki", "JUBILEE"),
        ("012", "MERU", "Daniel Wamalwa", "INDEPENDENT"),
        ("013", "THARAKA - NITHI", "Irene Kamau", "UDA"),
        ("013", "THARAKA - NITHI", "Caroline Odhiambo", "ODM"),
        ("014", "EMBU", "Brian Odhiambo", "WIPER"),
        ("014", "EMBU", "Jane Ochieng", "DAP-K"),
        ("015", "KITUI", "Mercy Otieno", "KANU"),
        ("015", "KITUI", "Michael Nyong'o", "WIPER"),
        ("016", "MACHAKOS", "Caroline Wamalwa", "INDEPENDENT"),
        ("016", "MACHAKOS", "Faith Ndungu", "ODM"),
        ("017", "MAKUENI", "Daniel Cheruiyot", "ODM"),
        ("017", "MAKUENI", "Lydia Mutua", "KANU"),
        ("018", "NYANDARUA", "Irene Kamau", "PNU"),
        ("018", "NYANDARUA", "Benard Wamalwa", "KANU"),
        ("019", "NYERI", "Faith Mwangi", "WIPER"),
        ("019", "NYERI", "Lucy Kiprotich", "JUBILEE"),
        ("020", "KIRINYAGA", "Samuel Kibet", "JUBILEE"),
        ("020", "KIRINYAGA", "James Wanjala", "UDA"),
        ("021", "MURANG'A", "Ruth Kibet", "UDA"),
        ("021", "MURANG'A", "Andrew Maina", "INDEPENDENT"),
        ("022", "KIAMBU", "Beatrice Cheruiyot", "WIPER"),
        ("022", "KIAMBU", "Irene Maina", "PNU"),
        ("023", "TURKANA", "Anthony Ochieng", "KANU"),
        ("023", "TURKANA", "Stella Nyong'o", "INDEPENDENT"),
        ("024", "WEST POKOT", "Esther Kariuki", "WIPER"),
        ("024", "WEST POKOT", "Kevin Mutua", "UDA"),
        ("025", "SAMBURU", "John Kibet", "WIPER"),
        ("025", "SAMBURU", "George Kariuki", "INDEPENDENT"),
        ("026", "TRANS NZOIA", "Martin Mwangi", "KANU"),
        ("026", "TRANS NZOIA", "Kevin Ochieng", "JUBILEE"),
        ("027", "UASIN GISHU", "Paul Barasa", "ODM"),
        ("027", "UASIN GISHU", "Phoebe Odhiambo", "DAP-K"),
        ("028", "ELGEYO/MARAKWET", "Ruth Maina", "PNU"),
        ("028", "ELGEYO/MARAKWET", "Beatrice Maina", "ODM"),
        ("029", "NANDI", "James Wanjala", "UDA"),
        ("029", "NANDI", "Lydia Maina", "INDEPENDENT"),
        ("030", "BARINGO", "Irene Omondi", "ODM"),
        ("030", "BARINGO", "Samuel Odhiambo", "INDEPENDENT"),
        ("031", "LAIKIPIA", "John Wamalwa", "UDA"),
        ("031", "LAIKIPIA", "Kevin Nyong'o", "WIPER"),
        ("032", "NAKURU", "Michael Wanjala", "PNU"),
        ("032", "NAKURU", "Hellen Mwangi", "UDA"),
        ("033", "NAROK", "Stephen Kiprotich", "INDEPENDENT"),
        ("033", "NAROK", "Susan Kiprotich", "ODM"),
        ("034", "KAJIADO", "Samuel Kibet", "INDEPENDENT"),
        ("034", "KAJIADO", "Lucy Kibet", "WIPER"),
        ("035", "KERICHO", "Joseph Odhiambo", "JUBILEE"),
        ("035", "KERICHO", "Daniel Njoroge", "DAP-K"),
        ("036", "BOMET", "Brian Barasa", "KANU"),
        ("036", "BOMET", "Peter Wanjala", "UDA"),
        ("037", "KAKAMEGA", "Diana Mwangi", "UDA"),
        ("037", "KAKAMEGA", "Agnes Kamau", "KANU"),
        ("038", "VIHIGA", "Stephen Barasa", "KANU"),
        ("038", "VIHIGA", "Joyce Omondi", "PNU"),
        ("039", "BUNGOMA", "George Nyong'o", "KANU"),
        ("039", "BUNGOMA", "Diana Barasa", "INDEPENDENT"),
        ("040", "BUSIA", "Dennis Kariuki", "PNU"),
        ("040", "BUSIA", "George Ndungu", "KANU"),
        ("041", "SIAYA", "Agnes Kibet", "KANU"),
        ("041", "SIAYA", "George Wanjala", "INDEPENDENT"),
        ("042", "KISUMU", "Peter Mwangi", "JUBILEE"),
        ("042", "KISUMU", "Anthony Kibet", "UDA"),
        ("043", "HOMA BAY", "Irene Kiprotich", "KANU"),
        ("043", "HOMA BAY", "Susan Kiprotich", "ODM"),
        ("044", "MIGORI", "George Kiptoo", "DAP-K"),
        ("044", "MIGORI", "George Kibet", "WIPER"),
        ("045", "KISII", "Hellen Ndungu", "ODM"),
        ("045", "KISII", "Mark Kibet", "DAP-K"),
        ("046", "NYAMIRA", "Faith Mutua", "DAP-K"),
        ("046", "NYAMIRA", "Samuel Maina", "INDEPENDENT"),
        ("047", "NAIROBI CITY", "Victor Ochieng", "PNU"),
        ("047", "NAIROBI CITY", "Mary Mutua", "DAP-K"),
    ]

    # Clear existing senator candidates
    existing_senators = Candidate.objects.filter(position=senator_position)
    print(
        f"Removing {existing_senators.count()} existing senator candidates...")
    existing_senators.delete()

    # County name mapping (CSV name -> Database name)
    county_mapping = {
        "MOMBASA": "Mombasa",
        "KWALE": "Kwale",
        "KILIFI": "Kilifi",
        "TANA RIVER": "Tana River",
        "LAMU": "Lamu",
        "TAITA TAVETA": "Taita Taveta",
        "GARISSA": "Garissa",
        "WAJIR": "Wajir",
        "MANDERA": "Mandera",
        "MARSABIT": "Marsabit",
        "ISIOLO": "Isiolo",
        "MERU": "Meru",
        "THARAKA - NITHI": "Tharaka Nithi",
        "EMBU": "Embu",
        "KITUI": "Kitui",
        "MACHAKOS": "Machakos",
        "MAKUENI": "Makueni",
        "NYANDARUA": "Nyandarua",
        "NYERI": "Nyeri",
        "KIRINYAGA": "Kirinyaga",
        "MURANG'A": "Murang'a",
        "KIAMBU": "Kiambu",
        "TURKANA": "Turkana",
        "WEST POKOT": "West Pokot",
        "SAMBURU": "Samburu",
        "TRANS NZOIA": "Trans Nzoia",
        "UASIN GISHU": "Uasin Gishu",
        "ELGEYO/MARAKWET": "Elgeyo Marakwet",
        "NANDI": "Nandi",
        "BARINGO": "Baringo",
        "LAIKIPIA": "Laikipia",
        "NAKURU": "Nakuru",
        "NAROK": "Narok",
        "KAJIADO": "Kajiado",
        "KERICHO": "Kericho",
        "BOMET": "Bomet",
        "KAKAMEGA": "Kakamega",
        "VIHIGA": "Vihiga",
        "BUNGOMA": "Bungoma",
        "BUSIA": "Busia",
        "SIAYA": "Siaya",
        "KISUMU": "Kisumu",
        "HOMA BAY": "Homa Bay",
        "MIGORI": "Migori",
        "KISII": "Kisii",
        "NYAMIRA": "Nyamira",
        "NAIROBI CITY": "Nairobi",
    }

    # Import new senator candidates
    imported_count = 0
    for county_code, county_name, candidate_name, party_name in senator_data:
        try:
            # Get county with mapping
            db_county_name = county_mapping.get(county_name, county_name)
            county = County.objects.get(name=db_county_name)

            # Get or create party
            party, created = Party.objects.get_or_create(
                name=party_name,
                defaults={'description': f'{party_name} Political Party'}
            )

            # Create candidate
            candidate = Candidate.objects.create(
                first_name=candidate_name.split(
                )[0] if ' ' in candidate_name else candidate_name,
                last_name=candidate_name.split(
                )[1] if ' ' in candidate_name else '',
                county=county,
                position=senator_position,
                party=party,
                id_number=f"SEN{county_code}{candidate_name[:3].upper()}"
            )

            imported_count += 1
            print(f"Imported: {candidate_name} - {party_name} ({county_name})")

        except County.DoesNotExist:
            print(
                f"Warning: County '{county_name}' (mapped to '{county_mapping.get(county_name, county_name)}') not found. Skipping {candidate_name}")
        except Exception as e:
            print(f"Error importing {candidate_name}: {e}")

    print(f"\n✅ Successfully imported {imported_count} senator candidates!")
    print(f"✅ Voters can now vote for their county's senator with verification!")
    return imported_count


if __name__ == "__main__":
    import_senator_candidates()
