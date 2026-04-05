from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User

from voting.models import (
    County,
    Constituency,
    Ward,
    PollingCenter,
    PollingStation,
    Position,
    Party,
    Candidate,
)


class Command(BaseCommand):
    help = (
        "Enforce election requirements: counts, candidate coverage, and presidential cleanup."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force-trim-wards",
            action="store_true",
            help="If wards exceed 1450, trim extras (and dependent records) to reach 1450.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.ensure_positions()
        self.ensure_parties()

        self.ensure_count_targets(force_trim_wards=options["force_trim_wards"])
        self.remove_banned_presidential_candidates()
        self.ensure_candidate_coverage()

        self.print_summary()

    def ensure_positions(self):
        positions = [
            ("PRESIDENT", "President of the Republic of Kenya"),
            ("GOVERNOR", "County Governor"),
            ("SENATOR", "Senator"),
            ("WOMEN_REP", "Women Representative"),
            ("MP", "Member of Parliament"),
            ("MCA", "Member of County Assembly"),
        ]

        for name, description in positions:
            Position.objects.get_or_create(
                name=name, defaults={"description": description})

    def ensure_parties(self):
        party_names = [
            "Independent Party",
            "Jubilee Party",
            "Orange Democratic Movement",
            "United Democratic Alliance",
            "Wiper Democratic Movement",
        ]

        for name in party_names:
            Party.objects.get_or_create(
                name=name,
                defaults={
                    "description": f"{name} political party",
                    "logo": "party_logos/default.png",
                },
            )

    def ensure_count_targets(self, force_trim_wards=False):
        county_count = County.objects.count()
        constituency_count = Constituency.objects.count()
        ward_count = Ward.objects.count()

        if county_count != 47:
            self.stdout.write(
                self.style.WARNING(
                    f"County count is {county_count}, expected 47. Add/remove manually if needed."
                )
            )

        if constituency_count != 290:
            self.stdout.write(
                self.style.WARNING(
                    f"Constituency count is {constituency_count}, expected 290. Add/remove manually if needed."
                )
            )

        if ward_count < 1450:
            self.create_missing_wards(1450 - ward_count)
        elif ward_count > 1450:
            if force_trim_wards:
                self.trim_extra_wards(ward_count - 1450)
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Ward count is {ward_count}. Run with --force-trim-wards to enforce exactly 1450."
                    )
                )

    def create_missing_wards(self, needed):
        self.stdout.write(f"Creating {needed} missing wards to reach 1450...")

        constituencies = list(Constituency.objects.order_by("id"))
        if not constituencies:
            self.stdout.write(self.style.ERROR(
                "No constituencies found. Cannot create wards."))
            return

        max_code_num = 0
        for code in Ward.objects.values_list("code", flat=True):
            try:
                max_code_num = max(max_code_num, int(code))
            except (TypeError, ValueError):
                continue

        created = 0
        idx = 0
        while created < needed:
            constituency = constituencies[idx % len(constituencies)]
            max_code_num += 1
            ward_code = f"{max_code_num:06d}"
            ward_name = f"{constituency.name} WARD AUTO {created + 1}"

            Ward.objects.create(
                name=ward_name,
                constituency=constituency,
                code=ward_code,
                registered_voters_2022=0,
                polling_centers=0,
                polling_stations=0,
                avg_voters_per_center=0,
                avg_voters_per_station=0,
            )

            created += 1
            idx += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} wards."))

    def trim_extra_wards(self, extra):
        self.stdout.write(f"Trimming {extra} extra wards to enforce 1450...")
        wards_to_delete = list(Ward.objects.order_by("-id")[:extra])

        for ward in wards_to_delete:
            ward.delete()

        self.stdout.write(self.style.SUCCESS(f"Trimmed {extra} wards."))

    def remove_banned_presidential_candidates(self):
        president = Position.objects.get(name="PRESIDENT")
        qs = Candidate.objects.filter(position=president)
        banned_qs = qs.filter(first_name__iregex=r"^(Raila|William)$") | qs.filter(
            last_name__iregex=r"^(Odinga|Ruto|Samoei Ruto|Amolo Odinga)$"
        )

        replacements = [
            ("Peter", "Mwangi"),
            ("Grace", "Wanjiku"),
            ("David", "Mutiso"),
            ("Anne", "Njeri"),
        ]

        updated_count = 0
        for idx, candidate in enumerate(banned_qs.order_by("id")):
            first_name, last_name = replacements[idx % len(replacements)]
            candidate.first_name = first_name
            candidate.last_name = last_name
            candidate.save(update_fields=["first_name", "last_name"])
            updated_count += 1

        if updated_count:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Replaced {updated_count} banned presidential candidate names."
                )
            )

        if not Candidate.objects.filter(position=president).exists():
            party = Party.objects.order_by("id").first()
            Candidate.objects.create(
                id_number="PRESAUTO001",
                first_name="Kenya",
                last_name="Unity",
                party=party,
                position=president,
                photo="candidate_photos/default.jpg",
            )
            self.stdout.write(self.style.SUCCESS(
                "Created fallback presidential candidate."))

    def ensure_candidate_coverage(self):
        party = Party.objects.order_by("id").first()
        positions = {p.name: p for p in Position.objects.all()}

        self.ensure_county_level_candidates(party, positions)
        self.ensure_constituency_level_candidates(party, positions)
        self.ensure_ward_level_candidates(party, positions)

    def ensure_county_level_candidates(self, party, positions):
        created = 0
        for county in County.objects.all():
            for pos_name in ["GOVERNOR", "SENATOR", "WOMEN_REP"]:
                if not Candidate.objects.filter(position=positions[pos_name], county=county).exists():
                    Candidate.objects.create(
                        id_number=f"{pos_name[:3]}AUTO{county.code}",
                        first_name=pos_name.title(),
                        last_name=f"{county.name} Candidate",
                        party=party,
                        position=positions[pos_name],
                        county=county,
                        photo="candidate_photos/default.jpg",
                    )
                    created += 1
        self.stdout.write(self.style.SUCCESS(
            f"County-level candidates added: {created}"))

    def ensure_constituency_level_candidates(self, party, positions):
        created = 0
        for constituency in Constituency.objects.select_related("county"):
            if not Candidate.objects.filter(
                position=positions["MP"], constituency=constituency
            ).exists():
                Candidate.objects.create(
                    id_number=f"MPAUTO{constituency.code}",
                    first_name="MP",
                    last_name=f"{constituency.name} Candidate",
                    party=party,
                    position=positions["MP"],
                    county=constituency.county,
                    constituency=constituency,
                    photo="candidate_photos/default.jpg",
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Constituency-level candidates added: {created}"))

    def ensure_ward_level_candidates(self, party, positions):
        created = 0
        for ward in Ward.objects.select_related("constituency", "constituency__county"):
            if not Candidate.objects.filter(position=positions["MCA"], ward=ward).exists():
                Candidate.objects.create(
                    id_number=f"MCAAUTO{ward.code}",
                    first_name="MCA",
                    last_name=f"{ward.name} Candidate",
                    party=party,
                    position=positions["MCA"],
                    county=ward.constituency.county,
                    constituency=ward.constituency,
                    ward=ward,
                    photo="candidate_photos/default.jpg",
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Ward-level candidates added: {created}"))

    def print_summary(self):
        self.stdout.write("Requirement summary:")
        self.stdout.write(f"  Counties: {County.objects.count()}")
        self.stdout.write(f"  Constituencies: {Constituency.objects.count()}")
        self.stdout.write(f"  Wards: {Ward.objects.count()}")

        president = Position.objects.get(name="PRESIDENT")
        presidential_names = list(
            Candidate.objects.filter(position=president).values_list(
                "first_name", "last_name")
        )
        self.stdout.write(f"  Presidential candidates: {presidential_names}")

        self.stdout.write(self.style.SUCCESS("Enforcement completed."))
