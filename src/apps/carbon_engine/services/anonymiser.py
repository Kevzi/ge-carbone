import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FECAnonymiser:
    """
    Service d'anonymisation des données du FEC (RGPD).
    Masque les données personnelles dans les libellés et tronque les comptes.
    """
    
    # Expression régulière pour détecter des motifs ressemblant à des noms ou données sensibles
    # (Ex: M. DUPONT, JEAN MARTIN, numéros de téléphone, etc.)
    # Ceci est une implémentation simplifiée. Un vrai NER (Spacy/CamemBERT) serait idéal en production.
    SENSITIVE_PATTERNS = [
        re.compile(r'\b(?:M\.|MME|MONSIEUR|MADAME|MLLE)\s+[A-Z]+\b', re.IGNORECASE),
        re.compile(r'\b[A-Z]{2,}\s+[A-Z]{2,}\b'), # Noms propres en majuscules (heuristique basique)
        re.compile(r'\b\d{10}\b'), # Numéros de téléphone français
        re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.IGNORECASE) # Emails
    ]

    @classmethod
    def truncate_compte(cls, compte_num: str, max_length: int = 4) -> str:
        """
        Tronque le numéro de compte pour éviter l'identification des tiers (ex: 401FOURN -> 4010).
        Garde 4 caractères pour préserver la nomenclature du PCG.
        """
        if not compte_num:
            return ""
        
        # On ne garde que les chiffres
        compte_digits = ''.join(filter(str.isdigit, str(compte_num)))
        
        if len(compte_digits) == 0:
            return str(compte_num)[:max_length]
            
        # Si le compte est plus court que 4 chiffres, on le pad avec des zéros
        if len(compte_digits) < max_length:
            return compte_digits.ljust(max_length, '0')
            
        return compte_digits[:max_length]

    @classmethod
    def anonymize_libelle(cls, libelle: str) -> str:
        """
        Masque les entités nommées ou données sensibles dans le libellé de l'écriture.
        """
        if not libelle:
            return ""
            
        anonymized = str(libelle)
        
        for pattern in cls.SENSITIVE_PATTERNS:
            anonymized = pattern.sub('[MASQUÉ]', anonymized)
            
        return anonymized

    @classmethod
    def prepare_feedback_data(cls, compte_num: str, libelle: str) -> tuple[str, str]:
        """
        Prépare les données pour la boucle de feedback en appliquant l'anonymisation RGPD.
        """
        anon_compte = cls.truncate_compte(compte_num)
        anon_libelle = cls.anonymize_libelle(libelle)
        
        return anon_compte, anon_libelle
