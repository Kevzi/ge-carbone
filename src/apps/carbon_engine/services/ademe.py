import logging
import requests
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from apps.carbon_engine.models import EmissionFactor

logger = logging.getLogger(__name__)


class ADEMEAPIError(Exception):
    """Exception raised for errors in the ADEME API."""
    pass


class ADEMESync:
    """Service pour synchroniser les facteurs d'émission avec l'API ADEME."""
    
    BASE_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/base-carboner/lines"
    
    def sync_factors(self, version=None):
        """
        Synchronise les facteurs depuis l'API ADEME.
        Si version n'est pas fourni, utilise un timestamp.
        """
        if not version:
            version = timezone.now().strftime("%Y-%m-%d-%H%M")
            
        logger.info(f"Début de la synchronisation ADEME (version: {version})")
        valid_from_date = timezone.now().date()
        
        url = self.BASE_URL
        params = {"size": 1000}
        created_or_updated = 0
        
        try:
            while url:
                response = requests.get(url, params=params if url == self.BASE_URL else None, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                for item in results:
                    identifiant = str(item.get("identifiant") or "").strip()
                    if not identifiant or identifiant == "None":
                        continue
                        
                    valeur_raw = item.get("valeur")
                    try:
                        valeur_dec = Decimal(str(valeur_raw)) if valeur_raw is not None else Decimal('0.0')
                    except (InvalidOperation, TypeError, ValueError):
                        valeur_dec = Decimal('0.0')
                        
                    unite = str(item.get("unite") or "").strip()
                    
                    val_euro = Decimal('0.0')
                    val_unit = None
                    
                    if unite.lower() in ['€', 'euros', 'euro']:
                        val_euro = valeur_dec
                    else:
                        val_unit = valeur_dec
                        val_euro = Decimal('0.0')

                    cat_str = str(item.get("categorie") or "").strip()
                    if cat_str.startswith("1"):
                        scope = 1
                    elif cat_str.startswith("2"):
                        scope = 2
                    else:
                        scope = 3
                        
                    try:
                        inc = int(item.get("incertitude") or 50)
                    except (ValueError, TypeError):
                        inc = 50
                    
                    _, created = EmissionFactor.objects.update_or_create(
                        ademe_id=identifiant,
                        version=version,
                        defaults={
                            'name': str(item.get("nom_base_francais") or "Inconnu")[:500],
                            'category': cat_str[:255],
                            'subcategory': str(item.get("sous_categorie") or "")[:255],
                            'value_kg_co2_per_euro': val_euro,
                            'value_kg_co2_per_unit': val_unit,
                            'unit': unite[:50],
                            'uncertainty_percent': inc,
                            'valid_from': valid_from_date,
                            'scope': scope
                        }
                    )
                    created_or_updated += 1
                
                url = data.get("next")
                
            logger.info(f"Synchronisation ADEME terminée : {created_or_updated} facteurs importés.")
            return created_or_updated
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation ADEME : {str(e)}")
            raise ADEMEAPIError(f"Erreur de l'API ADEME : {str(e)}") from e
