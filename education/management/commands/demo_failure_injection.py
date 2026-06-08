"""
IMPROVEMENT 7: Failure Injection Demo
Demonstrates graceful degradation and fallback behavior.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import random
import time


class Command(BaseCommand):
    help = 'Demonstrate failure injection and graceful degradation (IMPROVEMENT 7)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            choices=['database', 'external_api', 'timeout', 'all'],
            default='all',
            help='Failure scenario to demonstrate'
        )

    def handle(self, *args, **options):
        scenario = options['scenario']

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('IMPROVEMENT 7: Failure Injection Demo'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        if scenario in ['database', 'all']:
            self._demo_database_failure()

        if scenario in ['external_api', 'all']:
            self._demo_external_api_failure()

        if scenario in ['timeout', 'all']:
            self._demo_timeout_failure()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Demo complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 60))

    def _demo_database_failure(self):
        """Demonstrate database failure handling."""
        self.stdout.write(self.style.WARNING('\n[SCENARIO 1] Database Connection Failure'))
        self.stdout.write('-' * 60)

        from education.models import Student

        try:
            # Simulate database query
            self.stdout.write('Attempting to query students...')
            
            # Inject failure randomly
            if random.random() < 0.3:  # 30% failure rate
                raise Exception('Database connection timeout')
            
            students = Student.objects.all()[:5]
            self.stdout.write(self.style.SUCCESS(f'✓ Successfully retrieved {students.count()} students'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database query failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('→ Fallback: Using cached data or default values'))
            self.stdout.write(self.style.SUCCESS('✓ System continues to operate with degraded functionality'))

    def _demo_external_api_failure(self):
        """Demonstrate external API failure handling."""
        self.stdout.write(self.style.WARNING('\n[SCENARIO 2] External API Failure'))
        self.stdout.write('-' * 60)

        try:
            # Simulate external API call
            self.stdout.write('Calling external risk scoring API...')
            
            # Inject failure randomly
            if random.random() < 0.4:  # 40% failure rate
                raise ConnectionError('External API unreachable')
            
            # Simulate successful API response
            time.sleep(0.5)
            risk_score = random.uniform(0, 100)
            self.stdout.write(self.style.SUCCESS(f'✓ API returned risk score: {risk_score:.2f}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ External API call failed: {str(e)}'))
            self.stdout.write(self.style.WARNING('→ Fallback: Using local rule-based scoring'))
            
            # Fallback to local scoring
            from ai_engine.scoring import explainable_risk_score
            
            sample_data = {
                'attendance_rate': 85.0,
                'average_grade': 12.5,
                'behavior_incidents': 2,
                'missed_appointments': 1
            }
            
            result = explainable_risk_score(sample_data)
            self.stdout.write(self.style.SUCCESS(f'✓ Local scoring returned: {result["risk_score"]:.2f} ({result["risk_level"]})'))
            self.stdout.write(self.style.SUCCESS('✓ System continues with local fallback'))

    def _demo_timeout_failure(self):
        """Demonstrate timeout handling."""
        self.stdout.write(self.style.WARNING('\n[SCENARIO 3] Operation Timeout'))
        self.stdout.write('-' * 60)

        try:
            # Simulate long-running operation
            self.stdout.write('Generating comprehensive report (timeout: 3s)...')
            
            # Inject timeout randomly
            if random.random() < 0.5:  # 50% timeout rate
                time.sleep(0.5)
                raise TimeoutError('Operation exceeded timeout limit')
            
            time.sleep(1)
            self.stdout.write(self.style.SUCCESS('✓ Report generated successfully'))
            
        except TimeoutError as e:
            self.stdout.write(self.style.ERROR(f'✗ Operation timed out: {str(e)}'))
            self.stdout.write(self.style.WARNING('→ Fallback: Generating summary report instead'))
            
            # Fallback to quick summary
            time.sleep(0.2)
            self.stdout.write(self.style.SUCCESS('✓ Summary report generated (reduced scope)'))
            self.stdout.write(self.style.SUCCESS('✓ User receives partial results instead of complete failure'))

    def _demo_validation_failure(self):
        """Demonstrate input validation failure."""
        self.stdout.write(self.style.WARNING('\n[SCENARIO 4] Input Validation Failure'))
        self.stdout.write('-' * 60)

        test_inputs = [
            {'attendance_rate': 150.0, 'valid': False},  # Invalid: > 100
            {'attendance_rate': -10.0, 'valid': False},  # Invalid: < 0
            {'attendance_rate': 85.0, 'valid': True},    # Valid
        ]

        for test_input in test_inputs:
            try:
                self.stdout.write(f'\nValidating input: attendance_rate={test_input["attendance_rate"]}')
                
                # Validate
                if not 0 <= test_input['attendance_rate'] <= 100:
                    raise ValueError(f'Attendance rate must be between 0 and 100, got {test_input["attendance_rate"]}')
                
                self.stdout.write(self.style.SUCCESS('✓ Input validation passed'))
                
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'✗ Validation failed: {str(e)}'))
                self.stdout.write(self.style.WARNING('→ Fallback: Using default value (75.0)'))
                self.stdout.write(self.style.SUCCESS('✓ System continues with safe default'))
