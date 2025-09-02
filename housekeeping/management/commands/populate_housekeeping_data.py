from django.core.management.base import BaseCommand
from housekeeping.models import HousekeepingStatus

class Command(BaseCommand):
    help = 'Populate default housekeeping statuses'

    def handle(self, *args, **options):
        # Default housekeeping statuses with colors
        default_statuses = [
            {
                'status_name': 'CLEAN',
                'description': 'Room is clean and ready for guests',
                'color_code': '#28a745'
            },
            {
                'status_name': 'DIRTY',
                'description': 'Room needs cleaning after guest checkout',
                'color_code': '#dc3545'
            },
            {
                'status_name': 'IN_PROGRESS',
                'description': 'Room is currently being cleaned',
                'color_code': '#ffc107'
            },
            {
                'status_name': 'OUT_OF_ORDER',
                'description': 'Room is out of order and cannot be used',
                'color_code': '#6c757d'
            },
            {
                'status_name': 'MAINTENANCE',
                'description': 'Room requires maintenance work',
                'color_code': '#fd7e14'
            },
            {
                'status_name': 'INSPECTED',
                'description': 'Room has been cleaned and inspected',
                'color_code': '#17a2b8'
            },
        ]

        created_count = 0
        for status_data in default_statuses:
            status, created = HousekeepingStatus.objects.get_or_create(
                status_name=status_data['status_name'],
                defaults=status_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created status: {status.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Status already exists: {status.display_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new housekeeping statuses')
        )