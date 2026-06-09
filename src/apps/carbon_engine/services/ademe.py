import logging
import requests
import re
import uuid
from django.utils import timezone
from django.db import transaction
from decimal import Decimal, InvalidOperation
from apps.carbon_engine.models import EmissionFactor

logger = logging.getLogger(__name__)


class ADEMEAPIError(Exception):
    """Exception raised for errors in the ADEME API."""
    pass


class ADEMESync:
    """Service pour synchroniser les facteurs d'émission avec l'API ADEME."""
    
    BASE_URLS = [
        "https://data.ademe.fr/data-fair/api/v1/datasets/base-carboner/lines",
        "https://data.ademe.fr/data-fair/api/v1/datasets/base-empreinte/lines"
    ]
    
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
        
        # Move regex outside loop for performance (Patch 4)
        mc_pattern = re.compile(r'moyen-courrier', re.IGNORECASE)
        lc_pattern = re.compile(r'long-courrier', re.IGNORECASE)
        
        def _clean_aviation_bug(text, cat_str):
            # Scope workaround to Transport category only (Patch 3)
            if not text or cat_str != "Transport":
                return text
                
            has_mc = bool(mc_pattern.search(text))
            has_lc = bool(lc_pattern.search(text))
            
            if has_mc and not has_lc:
                return mc_pattern.sub("long-courrier", text) # Patch 7
            elif has_lc and not has_mc:
                return lc_pattern.sub("moyen-courrier", text)
            elif has_mc and has_lc:
                # Patch 8: use UUID for safe swap
                temp_mc = f"__TEMP_MC_{uuid.uuid4().hex}__"
                temp_lc = f"__TEMP_LC_{uuid.uuid4().hex}__"
                text = mc_pattern.sub(temp_mc, text)
                text = lc_pattern.sub(temp_lc, text)
                text = text.replace(temp_mc, "long-courrier")
                text = text.replace(temp_lc, "moyen-courrier")
            return text
            
        try:
            with transaction.atomic(): # Patch 2
                # Marquer TOUTES les anciennes versions comme archivées avant le sync (Patch 5)
                # Les facteurs synchronisés seront remis à is_archived=False via update_or_create
                EmissionFactor.objects.update(is_archived=True)
                
                for base_url in self.BASE_URLS:
                    url = base_url
                while url:
                    response = requests.get(url, params=params if url == base_url else None, timeout=30)
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
                    
                    nom_fr = str(item.get("nom_base_francais") or "Inconnu")[:500]
                    sous_cat = str(item.get("sous_categorie") or "")[:255]
                    
                    nom_fr = _clean_aviation_bug(nom_fr, cat_str)
                    sous_cat = _clean_aviation_bug(sous_cat, cat_str)
                    
                    # Patch 9: ID Collision Between Datasets
                    dataset_prefix = "carboner" if "base-carboner" in base_url else "empreinte"
                    unique_id = f"{dataset_prefix}-{identifiant}"
                    
                    _, created = EmissionFactor.objects.update_or_create(
                        ademe_id=unique_id,
                        version=version,
                        defaults={
                            'name': nom_fr,
                            'category': cat_str[:255],
                            'subcategory': sous_cat,
                            'value_kg_co2_per_euro': val_euro,
                            'value_kg_co2_per_unit': val_unit,
                            'unit': unite[:50],
                            'uncertainty_percent': inc,
                            'valid_from': valid_from_date,
                            'scope': scope,
                            'is_archived': False
                        }
                    )
                    created_or_updated += 1
                
                url = data.get("next")
                
            logger.info(f"Synchronisation ADEME terminée : {created_or_updated} facteurs importés.")
            return created_or_updated
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation ADEME : {str(e)}")
            raise ADEMEAPIError(f"Erreur de l'API ADEME : {str(e)}") from e
