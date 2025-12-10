from django.core.management.base import BaseCommand
from app.models import Club

class Command(BaseCommand):
    help = 'Creates the initial clubs'

    def handle(self, *args, **options):
        clubs = [
            'Music Club',
            'Cybersecurity Club',
            'Making Friends',
            'Book Club',
            'Lunch',
            'Movie Nights',
            'Art Club',
            'General',
            'Study Group',
            'Tennis Club',
            'Basketball Club',
            'Soccer Club',
            'Chess Club',
        ]
        
        created_count = 0
        for club_name in clubs:
            club, created = Club.objects.get_or_create(name=club_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created club: {club_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Club already exists: {club_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new clubs!')
        )

