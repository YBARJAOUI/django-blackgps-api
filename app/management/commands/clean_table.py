from django.core.management.base import BaseCommand
from app.models import TrackerData

class Command(BaseCommand):
    help = 'Vide la table TrackerData de la base de données'

    def handle(self, *args, **options):
        TrackerData.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('La table TrackerData a été vidée avec succès.'))
