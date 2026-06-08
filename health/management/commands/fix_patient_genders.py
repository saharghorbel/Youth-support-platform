"""
Management command to fix patient genders based on Tunisian first names.
Ensures male names have gender='M' and female names have gender='F'.
"""
from django.core.management.base import BaseCommand
from health.models import Patient


class Command(BaseCommand):
    help = 'Fix patient genders based on Tunisian first name lists'

    # Tunisian male first names
    TUNISIAN_FIRST_NAMES_MALE = [
        'Mohamed', 'Ahmed', 'Ali', 'Youssef', 'Mehdi', 'Amine', 'Karim',
        'Rami', 'Sami', 'Tarek', 'Walid', 'Zied', 'Hamza', 'Bilel', 'Fares'
    ]

    # Tunisian female first names
    TUNISIAN_FIRST_NAMES_FEMALE = [
        'Fatma', 'Amira', 'Salma', 'Nour', 'Ines', 'Mariem', 'Yasmine',
        'Leila', 'Hana', 'Rim', 'Sarra', 'Wafa', 'Dorra', 'Ghada', 'Rania'
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('FIXING PATIENT GENDERS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        fixed_count = 0
        unchanged_count = 0

        # Get all patients
        patients = Patient.objects.all()

        for patient in patients:
            original_gender = patient.gender
            new_gender = None

            # Check if first name is in male list
            if patient.first_name in self.TUNISIAN_FIRST_NAMES_MALE:
                new_gender = 'M'
            # Check if first name is in female list
            elif patient.first_name in self.TUNISIAN_FIRST_NAMES_FEMALE:
                new_gender = 'F'

            # Update if gender needs to be changed
            if new_gender and new_gender != original_gender:
                patient.gender = new_gender
                patient.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed: {patient.first_name} {patient.last_name} → {new_gender}'
                    )
                )
            else:
                unchanged_count += 1
                self.stdout.write(
                    f'OK: {patient.first_name} {patient.last_name} ({patient.gender})'
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'Total patients: {patients.count()}')
        self.stdout.write(self.style.SUCCESS(f'Fixed: {fixed_count}'))
        self.stdout.write(f'Unchanged: {unchanged_count}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Gender fix complete!'))
