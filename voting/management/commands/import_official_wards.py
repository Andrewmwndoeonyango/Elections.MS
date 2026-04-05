from django.core.management.base import BaseCommand
from voting.models import County, Constituency, Ward
import csv
import time


class Command(BaseCommand):
    help = 'Import official IEBC ward data from CSV file'

    def handle(self, *args, **options):
        self.stdout.write('=== IMPORTING OFFICIAL IEBC WARD DATA ===')
        start_time = time.time()

        # Clear existing wards to start fresh with official data
        self.stdout.write('Clearing existing wards...')
        Ward.objects.all().delete()

        # Read and import the official ward data
        csv_file_path = 'additional_wards_data.csv'

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                added_count = 0
                skipped_count = 0

                for row in reader:
                    try:
                        # Get constituency (constituency codes are unique, so we don't need county filter)
                        constituency = Constituency.objects.get(
                            code=row['constituency_code'])

                        # Create ward with official data
                        Ward.objects.create(
                            code=row['ward_code'],
                            name=row['ward_name'],
                            constituency=constituency,
                            registered_voters_2022=int(
                                row['ward_registered_voters_2022']),
                            polling_centers=int(
                                row['allocated_polling_centers']),
                            polling_stations=int(
                                row['allocated_polling_stations']),
                            avg_voters_per_center=float(
                                row['avg_voters_per_center_est']),
                            avg_voters_per_station=float(
                                row['avg_voters_per_station_est'])
                        )

                        added_count += 1

                        if added_count % 100 == 0:
                            self.stdout.write(
                                f'Imported {added_count} wards...')

                    except Constituency.DoesNotExist:
                        self.stdout.write(
                            f"⚠️ Constituency {row['constituency_code']} not found, skipping...")
                        skipped_count += 1
                    except Exception as e:
                        self.stdout.write(
                            f"⚠️ Error importing ward {row['ward_code']}: {e}")
                        skipped_count += 1

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'❌ CSV file {csv_file_path} not found!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'❌ Error reading CSV file: {e}'))
            return

        end_time = time.time()

        self.stdout.write(f'\n=== IMPORT RESULTS ===')
        self.stdout.write(f'Wards imported: {added_count}')
        self.stdout.write(f'Wards skipped: {skipped_count}')
        self.stdout.write(f'Time taken: {end_time - start_time:.2f} seconds')

        # Verify final count
        final_count = Ward.objects.count()
        self.stdout.write(f'Final ward count: {final_count}')

        if final_count >= 1400:  # Expecting close to 1450
            self.stdout.write(self.style.SUCCESS(
                '🎉 Official IEBC ward data imported successfully!'))
        else:
            self.stdout.write(self.style.WARNING(
                f'⚠️ Only {final_count} wards imported (expected ~1450)'))
