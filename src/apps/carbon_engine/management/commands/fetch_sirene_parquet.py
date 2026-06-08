import os
import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Télécharge le fichier stock SIRENE au format Apache Parquet depuis data.gouv.fr'

    def handle(self, *args, **options):
        # URL fictive ou réelle du dataset Parquet (ici on prend le dernier standard de data.gouv)
        PARQUET_URL = "https://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.parquet"
        
        # Ensure media directory exists
        media_dir = os.path.join(settings.BASE_DIR, 'media', 'sirene')
        os.makedirs(media_dir, exist_ok=True)
        
        parquet_path = os.path.join(media_dir, 'StockEtablissement_utf8.parquet')
        
        self.stdout.write(f"Téléchargement du fichier Sirene Parquet depuis {PARQUET_URL}...")
        
        try:
            # Note: in a real environment, use streaming download for large files
            response = requests.get(PARQUET_URL, stream=True)
            if response.status_code == 200:
                with open(parquet_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.stdout.write(self.style.SUCCESS(f"Téléchargement terminé : {parquet_path}"))
            else:
                self.stdout.write(self.style.ERROR(f"Erreur HTTP {response.status_code} lors du téléchargement"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors du téléchargement: {str(e)}"))
