from django.core.management.base import BaseCommand
from django.db import models
from voting.models import County, Constituency, Ward, PollingCenter, PollingStation
import time

class Command(BaseCommand):
    help = 'Final verification of Kenya electoral hierarchy'

    def handle(self, *args, **options):
        self.stdout.write('=== FINAL KENYA ELECTORAL HIERARCHY VERIFICATION ===')
        start_time = time.time()

        self.stdout.write('Step 1: Verifying complete hierarchy...')
        self._verify_hierarchy()

        self.stdout.write('Step 2: Analyzing data distribution...')
        self._analyze_distribution()

        self.stdout.write('Step 3: Checking data integrity...')
        self._check_integrity()

        self.stdout.write('Step 4: Generating summary report...')
        self._generate_summary()

        end_time = time.time()
        self.stdout.write(f'=== VERIFICATION COMPLETED IN {end_time - start_time:.2f} SECONDS ===')

    def _verify_hierarchy(self):
        """Verify the complete hierarchy counts"""
        counties = County.objects.count()
        constituencies = Constituency.objects.count()
        wards = Ward.objects.count()
        polling_centers = PollingCenter.objects.count()
        polling_stations = PollingStation.objects.count()

        self.stdout.write(f'\n📊 HIERARCHY COUNTS:')
        self.stdout.write(f'  Counties: {counties}/47 {"✅" if counties == 47 else "❌"}')
        self.stdout.write(f'  Constituencies: {constituencies}/290 {"✅" if constituencies == 290 else "❌"}')
        self.stdout.write(f'  Wards: {wards}/1450 {"✅" if wards == 1450 else "❌"}')
        self.stdout.write(f'  Polling Centers: {polling_centers} {"✅" if polling_centers >= 24000 else "❌"}')
        self.stdout.write(f'  Polling Stations: {polling_stations} {"✅" if polling_stations >= 46000 else "❌"}')

    def _analyze_distribution(self):
        """Analyze distribution of entities"""
        self.stdout.write(f'\n📈 DISTRIBUTION ANALYSIS:')
        
        # Ward distribution
        constituency_ward_counts = []
        for const in Constituency.objects.all():
            ward_count = Ward.objects.filter(constituency=const).count()
            constituency_ward_counts.append(ward_count)
        
        avg_wards = sum(constituency_ward_counts) / len(constituency_ward_counts)
        min_wards = min(constituency_ward_counts)
        max_wards = max(constituency_ward_counts)
        
        self.stdout.write(f'  Wards per constituency:')
        self.stdout.write(f'    Average: {avg_wards:.1f}')
        self.stdout.write(f'    Minimum: {min_wards}')
        self.stdout.write(f'    Maximum: {max_wards}')
        
        # Polling center distribution
        ward_center_counts = []
        for ward in Ward.objects.all():
            center_count = PollingCenter.objects.filter(ward=ward).count()
            ward_center_counts.append(center_count)
        
        avg_centers = sum(ward_center_counts) / len(ward_center_counts)
        min_centers = min(ward_center_counts)
        max_centers = max(ward_center_counts)
        
        self.stdout.write(f'  Polling centers per ward:')
        self.stdout.write(f'    Average: {avg_centers:.1f}')
        self.stdout.write(f'    Minimum: {min_centers}')
        self.stdout.write(f'    Maximum: {max_centers}')

    def _check_integrity(self):
        """Check data integrity and relationships"""
        self.stdout.write(f'\n🔍 DATA INTEGRITY CHECK:')
        
        # Check for orphaned records
        orphaned_wards = Ward.objects.filter(constituency__isnull=True).count()
        orphaned_centers = PollingCenter.objects.filter(ward__isnull=True).count()
        orphaned_stations = PollingStation.objects.filter(center__isnull=True).count()
        
        self.stdout.write(f'  Orphaned wards: {orphaned_wards} {"✅" if orphaned_wards == 0 else "❌"}')
        self.stdout.write(f'  Orphaned polling centers: {orphaned_centers} {"✅" if orphaned_centers == 0 else "❌"}')
        self.stdout.write(f'  Orphaned polling stations: {orphaned_stations} {"✅" if orphaned_stations == 0 else "❌"}')
        
        # Check for unique codes
        duplicate_ward_codes = Ward.objects.values('code').annotate(count=models.Count('code')).filter(count__gt=1).count()
        duplicate_center_codes = PollingCenter.objects.values('code').annotate(count=models.Count('code')).filter(count__gt=1).count()
        duplicate_station_codes = PollingStation.objects.values('code').annotate(count=models.Count('code')).filter(count__gt=1).count()
        
        self.stdout.write(f'  Duplicate ward codes: {duplicate_ward_codes} {"✅" if duplicate_ward_codes == 0 else "❌"}')
        self.stdout.write(f'  Duplicate center codes: {duplicate_center_codes} {"✅" if duplicate_center_codes == 0 else "❌"}')
        self.stdout.write(f'  Duplicate station codes: {duplicate_station_codes} {"✅" if duplicate_station_codes == 0 else "❌"}')

    def _generate_summary(self):
        """Generate final summary"""
        self.stdout.write(f'\n📋 FINAL SUMMARY:')
        
        # Calculate totals
        total_voters = Ward.objects.aggregate(models.Sum('registered_voters_2022'))['registered_voters_2022__sum'] or 0
        total_centers = PollingCenter.objects.aggregate(models.Sum('registered_voters'))['registered_voters__sum'] or 0
        total_stations = PollingStation.objects.aggregate(models.Sum('registered_voters'))['registered_voters__sum'] or 0
        
        self.stdout.write(f'  Total registered voters (wards): {total_voters:,}')
        self.stdout.write(f'  Total registered voters (centers): {total_centers:,}')
        self.stdout.write(f'  Total registered voters (stations): {total_stations:,}')
        
        # Sample hierarchy display
        self.stdout.write(f'\n🗺️ SAMPLE HIERARCHY:')
        for county in County.objects.all()[:3]:  # Show first 3 counties
            self.stdout.write(f'  {county.name} County ({county.code}):')
            for const in Constituency.objects.filter(county=county)[:2]:  # Show first 2 constituencies
                ward_count = Ward.objects.filter(constituency=const).count()
                center_count = PollingCenter.objects.filter(ward__constituency=const).count()
                station_count = PollingStation.objects.filter(center__ward__constituency=const).count()
                self.stdout.write(f'    {const.name} ({const.code}): {ward_count} wards, {center_count} centers, {station_count} stations')
        
        # Final status
        counties = County.objects.count()
        constituencies = Constituency.objects.count()
        wards = Ward.objects.count()
        
        if counties == 47 and constituencies == 290 and wards == 1450:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 KENYA ELECTORAL HIERARCHY COMPLETE & VERIFIED!'))
            self.stdout.write(self.style.SUCCESS(f'   Ready for production use with {total_voters:,} registered voters'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️ Hierarchy needs attention'))
