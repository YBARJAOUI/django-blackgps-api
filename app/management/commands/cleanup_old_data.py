from django.core.management.base import BaseCommand
from pathlib import Path
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Deletes folders older than 3 months'

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent / 'trackers'
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)

        for folder in base_dir.iterdir():
            if folder.is_dir():
                folder_date = datetime.strptime(folder.name, '%Y-%m-%d')
                if folder_date < three_months_ago:
                    self.stdout.write(f'Deleting folder {folder}')
                    for item in folder.iterdir():
                        item.unlink()
                    folder.rmdir()

        self.stdout.write(self.style.SUCCESS('Old folders deleted successfully.'))
