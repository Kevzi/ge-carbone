from typing import List, Dict, Optional
from django.contrib.postgres.search import TrigramSimilarity
from apps.carbon_engine.models import SireneStock

class SiretisationService:
    """
    Service for resolving supplier NAF codes using trigram similarity against Sirene data.
    """
    
    NAF_MAPPING = {
        # Agriculture et Agroalimentaire
        "01": "Produits de l'agriculture et de la pêche",
        "02": "Produits de l'agriculture et de la pêche",
        "03": "Produits de l'agriculture et de la pêche",
        "10": "Produits agro-alimentaires et boissons",
        "11": "Produits agro-alimentaires et boissons",

        # Industrie manufacturière
        "13": "Textile",
        "16": "Bois",
        "17": "Papier, carton et articles en papier ou en carton",
        "20": "Plastiques et autres produits chimiques",
        "22": "Plastiques et autres produits chimiques",
        "23": "Produits minéraux non métallique",
        "24": "Métaux et produits métalliques",
        "26": "Informatique et équipement de bureau",
        "27": "Équipements électriques",
        "28": "Machines et équipements",
        "29": "Véhicules automobiles et autres matériel de transport",
        "31": "Mobilier",
        "32": "Autres produits manufacturés",

        # Eau et Déchets
        "36": "Eau, traitement et distribution d'eau",
        "38": "Traitement des déchets",

        # Construction et Bâtiments
        "41": "Bâtiments et ouvrages d'art",
        "42": "Bâtiments et ouvrages d'art",
        "43": "Bâtiments et ouvrages d'art",

        # Transports
        "49": "Transport terrestre", 
        "50": "Transport maritime et fluvial",
        "51": "Transport aérien",

        # Services
        "56": "Restauration",
        "62": "Autres services informatiques"
    }

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def find_nafs_batch(self, fournisseurs_noms: List[str]) -> Dict[str, str]:
        """
        Find NAF codes for a batch of supplier names.
        By operating on unique names only, we avoid doing redundant queries per row.
        """
        results = {}
        unique_noms = set(n for n in fournisseurs_noms if n and len(n.strip()) >= 3)
        
        for nom in unique_noms:
            # Query the best matching SireneStock entry using TrigramSimilarity
            match = SireneStock.objects.annotate(
                similarity=TrigramSimilarity('denomination', nom)
            ).filter(
                similarity__gt=self.threshold
            ).order_by('-similarity').first()
            
            if match:
                results[nom] = match.naf_code
                
        return results

    def get_ademe_category_for_naf(self, naf_code: str) -> Optional[str]:
        """
        Map a NAF code to an ADEME category using the first two digits (division).
        """
        if not naf_code or len(naf_code) < 2:
            return None
        division = naf_code[:2]
        return self.NAF_MAPPING.get(division)
