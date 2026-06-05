"""
Carbon Engine services - PCG to ADEME mapping and CO2 calculation.
"""
import re
from decimal import Decimal
from typing import Optional, List, Tuple
from dataclasses import dataclass
import logging

from apps.carbon_engine.models import EmissionFactor, PCGMapping, CarbonEntry
from apps.fec_parser.services import FECRow

logger = logging.getLogger(__name__)


# Default emission factors when no specific mapping found
DEFAULT_EMISSION_FACTOR = Decimal('0.1')  # 0.1 kg CO2e per euro (conservative)


@dataclass
class CarbonCalculationResult:
    """Result of carbon calculation for a FEC row."""
    fec_line_number: int
    compte_num: str
    ecriture_lib: str
    debit: Decimal
    credit: Decimal
    amount: Decimal
    emission_factor_id: Optional[int]
    emission_factor_name: str
    emission_factor_value: Decimal
    co2_kg: Decimal
    scope: int
    dqr: int
    mapping_method: str
    deflator_factor: Decimal = Decimal('1.0')


class PCGMappingService:
    """
    Service for mapping PCG accounts to ADEME emission factors.
    Uses hierarchical matching: exact → prefix → NLP → fallback.
    """
    
    # PCG Class 6 categories with typical emission factors
    PCG_CATEGORY_DEFAULTS = {
        '601': ('Achats matières premières', 3, Decimal('0.3')),
        '602': ('Achats autres approvisionnements', 3, Decimal('0.2')),
        '604': ('Achats études et prestations', 3, Decimal('0.1')),
        '605': ('Achats matériel équipement', 3, Decimal('0.4')),
        '606': ('Achats non stockés', 3, Decimal('0.15')),
        '607': ('Achats marchandises', 3, Decimal('0.25')),
        '61': ('Services extérieurs', 3, Decimal('0.08')),
        '611': ('Sous-traitance générale', 3, Decimal('0.12')),
        '613': ('Locations', 3, Decimal('0.05')),
        '615': ('Entretien réparations', 3, Decimal('0.1')),
        '616': ('Primes assurance', 3, Decimal('0.02')),
        '617': ('Études recherches', 3, Decimal('0.05')),
        '618': ('Divers services', 3, Decimal('0.08')),
        '62': ('Autres services extérieurs', 3, Decimal('0.1')),
        '621': ('Personnel extérieur', 3, Decimal('0.05')),
        '622': ('Rémunérations intermédiaires', 3, Decimal('0.03')),
        '623': ('Publicité publications', 3, Decimal('0.12')),
        '624': ('Transports', 3, Decimal('0.35')),
        '625': ('Déplacements missions', 3, Decimal('0.25')),
        '626': ('Frais postaux télécoms', 3, Decimal('0.03')),
        '627': ('Services bancaires', 3, Decimal('0.01')),
        '628': ('Divers', 3, Decimal('0.08')),
        '63': ('Impôts taxes', 3, Decimal('0.01')),
        '64': ('Charges personnel', 3, Decimal('0.0')),  # Scope 3 cat 7 if included
        '65': ('Autres charges gestion', 3, Decimal('0.05')),
        '66': ('Charges financières', 3, Decimal('0.0')),
        '67': ('Charges exceptionnelles', 3, Decimal('0.05')),
        '68': ('Dotations amortissements', 3, Decimal('0.0')),
    }
    
    # NLP keywords for better categorization
    NLP_KEYWORDS = {
        # Transport
        ('sncf', 'tgv', 'train', 'rail'): ('Transport ferroviaire', 3, Decimal('0.03')),
        ('avion', 'air france', 'easyjet', 'vol', 'flight'): ('Transport aérien', 3, Decimal('0.25')),
        ('uber', 'taxi', 'vtc'): ('Transport VTC', 3, Decimal('0.15')),
        ('essence', 'carburant', 'diesel', 'gasoil'): ('Carburant véhicules', 1, Decimal('2.7')),
        ('péage', 'autoroute'): ('Transport routier', 3, Decimal('0.12')),
        
        # Energy
        ('électricité', 'edf', 'engie', 'kwh'): ('Électricité', 2, Decimal('0.05')),
        ('gaz', 'chauffage'): ('Gaz naturel', 1, Decimal('0.2')),
        
        # IT/Telecom
        ('cloud', 'aws', 'azure', 'google cloud', 'ovh'): ('Cloud computing', 3, Decimal('0.08')),
        ('téléphone', 'mobile', 'sfr', 'orange', 'bouygues'): ('Télécommunications', 3, Decimal('0.02')),
        
        # Office
        ('papier', 'imprimerie', 'impression'): ('Papeterie', 3, Decimal('0.8')),
        ('informatique', 'ordinateur', 'pc', 'laptop'): ('Équipement IT', 3, Decimal('0.5')),
        
        # Food
        ('restaurant', 'repas', 'traiteur', 'catering'): ('Restauration', 3, Decimal('0.5')),
        ('hôtel', 'hébergement', 'nuit'): ('Hébergement', 3, Decimal('0.02')),
    }
    
    def __init__(self):
        self._mapping_cache = {}
        self._factor_cache = {}
    
    def get_emission_factor(self, compte_num: str, ecriture_lib: str = '') -> Tuple[Optional[EmissionFactor], str, int]:
        """
        Get emission factor for a PCG account.
        
        Returns:
            Tuple of (EmissionFactor or None, mapping_method, dqr_score)
        """
        # 1. Try exact match from database
        factor, method = self._try_db_mapping(compte_num)
        if factor:
            return factor, method, 4  # Good DQR
        
        # 2. Try NLP on libellé
        factor, method, dqr = self._try_nlp_mapping(ecriture_lib)
        if factor:
            return factor, method, dqr
        
        # 3. Try prefix matching from defaults
        factor, method = self._try_prefix_mapping(compte_num)
        if factor:
            return factor, method, 3  # Medium DQR
        
        # 4. Fallback
        return None, 'fallback', 1  # Low DQR
    
    def _try_db_mapping(self, compte_num: str) -> Tuple[Optional[EmissionFactor], str]:
        """Try to find mapping in database."""
        # Check cache
        if compte_num in self._mapping_cache:
            return self._mapping_cache[compte_num], 'pcg_exact'
        
        # Try exact match
        try:
            mapping = PCGMapping.objects.filter(
                pcg_prefix=compte_num
            ).select_related('emission_factor').first()
            
            if mapping:
                self._mapping_cache[compte_num] = mapping.emission_factor
                return mapping.emission_factor, 'pcg_exact'
        except Exception:
            pass
        
        # Try progressively shorter prefixes
        for length in range(len(compte_num) - 1, 1, -1):
            prefix = compte_num[:length]
            try:
                mapping = PCGMapping.objects.filter(
                    pcg_prefix=prefix
                ).select_related('emission_factor').order_by('-priority').first()
                
                if mapping:
                    self._mapping_cache[compte_num] = mapping.emission_factor
                    return mapping.emission_factor, 'pcg_prefix'
            except Exception:
                pass
        
        return None, ''
    
    def _try_nlp_mapping(self, ecriture_lib: str) -> Tuple[Optional[EmissionFactor], str, int]:
        """Try to find mapping based on NLP keywords."""
        if not ecriture_lib:
            return None, '', 0
        
        lib_lower = ecriture_lib.lower()
        
        for keywords, (name, scope, value) in self.NLP_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lib_lower:
                    # Create a virtual emission factor
                    factor = EmissionFactor(
                        name=name,
                        value_kg_co2_per_euro=value,
                        scope=scope,
                        category=name
                    )
                    return factor, 'nlp', 4  # Good DQR for NLP match
        
        return None, '', 0
    
    def _try_prefix_mapping(self, compte_num: str) -> Tuple[Optional[EmissionFactor], str]:
        """Try to find mapping based on PCG prefix defaults."""
        # Try progressively shorter prefixes
        for length in range(len(compte_num), 1, -1):
            prefix = compte_num[:length]
            if prefix in self.PCG_CATEGORY_DEFAULTS:
                name, scope, value = self.PCG_CATEGORY_DEFAULTS[prefix]
                factor = EmissionFactor(
                    name=name,
                    value_kg_co2_per_euro=value,
                    scope=scope,
                    category=name
                )
                return factor, 'pcg_prefix'
        
        return None, ''


class CarbonCalculator:
    """
    Calculates CO2 emissions from FEC rows.
    """
    
    def __init__(self):
        self.mapping_service = PCGMappingService()
        self._deflators_cache = {}
        self._load_deflators()
        
    def _load_deflators(self):
        """Pre-load deflators in memory for fast lookup."""
        try:
            from apps.carbon_engine.models import InseeDeflator
            for d in InseeDeflator.objects.filter(naf_code__isnull=True):
                if d.year in self._deflators_cache:
                    logger.warning(f"Duplicate global deflator for year {d.year}")
                else:
                    self._deflators_cache[d.year] = d.index_value
        except Exception as e:
            logger.warning(f"Failed to load deflators: {e}")

    def get_deflator_factor(self, ecriture_year: int, ref_year: int) -> Decimal:
        if ecriture_year == ref_year:
            return Decimal('1.0')
            
        ref_index = self._deflators_cache.get(ref_year)
        row_index = self._deflators_cache.get(ecriture_year)
        
        if ref_index is None:
            logger.warning(f"No deflator for year {ref_year}, using factor 1.0")
        if row_index is None:
            logger.warning(f"No deflator for year {ecriture_year}, using factor 1.0")
            
        if ref_index is not None and row_index is not None and row_index != 0:
            return Decimal(ref_index) / Decimal(row_index)
            
        return Decimal('1.0')
    
    def calculate_row(self, row: FECRow) -> CarbonCalculationResult:
        """
        Calculate CO2 emissions for a single FEC row.
        """
        # Get net amount (only count expenses, class 6)
        amount = row.debit - row.credit
        
        # Only calculate for expense accounts (class 6)
        if not row.compte_num.startswith('6'):
            return CarbonCalculationResult(
                fec_line_number=row.line_number,
                compte_num=row.compte_num,
                ecriture_lib=row.ecriture_lib,
                debit=row.debit,
                credit=row.credit,
                amount=amount,
                emission_factor_id=None,
                emission_factor_name='Non applicable',
                emission_factor_value=Decimal('0'),
                co2_kg=Decimal('0'),
                scope=0,
                dqr=0,
                mapping_method='excluded'
            )
        
        # Get emission factor
        factor, method, dqr = self.mapping_service.get_emission_factor(
            row.compte_num,
            row.ecriture_lib
        )
        
        if factor:
            emission_value = factor.value_kg_co2_per_euro
            emission_name = factor.name
            scope = factor.scope
            factor_id = factor.id if factor.id else None
            
            # Application du déflateur Insee
            ecriture_year = row.ecriture_date.year if row.ecriture_date else None
            ref_year = factor.valid_from.year if getattr(factor, 'valid_from', None) else None
            
            if ecriture_year and ref_year and getattr(factor, 'unit', None) == '€':
                deflator_factor = self.get_deflator_factor(ecriture_year, ref_year)
            else:
                deflator_factor = Decimal('1.0')
        else:
            # Use default fallback
            emission_value = DEFAULT_EMISSION_FACTOR
            emission_name = 'Fallback moyen'
            scope = 3
            factor_id = None
            dqr = 1
            deflator_factor = Decimal('1.0')
        
        # Calculate CO2
        adjusted_amount = abs(amount) * deflator_factor
        co2_kg = adjusted_amount * emission_value
        
        return CarbonCalculationResult(
            fec_line_number=row.line_number,
            compte_num=row.compte_num,
            ecriture_lib=row.ecriture_lib,
            debit=row.debit,
            credit=row.credit,
            amount=amount,
            emission_factor_id=factor_id,
            emission_factor_name=emission_name,
            emission_factor_value=emission_value,
            co2_kg=co2_kg,
            scope=scope,
            dqr=dqr,
            mapping_method=method,
            deflator_factor=deflator_factor
        )
    
    def calculate_batch(self, rows: List[FECRow]) -> List[CarbonCalculationResult]:
        """
        Calculate CO2 emissions for a batch of FEC rows.
        """
        return [self.calculate_row(row) for row in rows]
    
    def aggregate_results(self, results: List[CarbonCalculationResult]) -> dict:
        """
        Aggregate carbon calculation results by scope.
        """
        totals = {
            'total_co2_kg': Decimal('0'),
            'scope1_co2_kg': Decimal('0'),
            'scope2_co2_kg': Decimal('0'),
            'scope3_co2_kg': Decimal('0'),
            'total_rows': 0,
            'calculated_rows': 0,
            'average_dqr': Decimal('0'),
            'by_category': {},
        }
        
        dqr_sum = 0
        dqr_count = 0
        
        for result in results:
            if result.mapping_method == 'excluded':
                continue
            
            totals['total_co2_kg'] += result.co2_kg
            totals['total_rows'] += 1
            
            if result.co2_kg > 0:
                totals['calculated_rows'] += 1
                dqr_sum += result.dqr
                dqr_count += 1
            
            if result.scope == 1:
                totals['scope1_co2_kg'] += result.co2_kg
            elif result.scope == 2:
                totals['scope2_co2_kg'] += result.co2_kg
            elif result.scope == 3:
                totals['scope3_co2_kg'] += result.co2_kg
            
            # Aggregate by category
            category = result.emission_factor_name
            if category not in totals['by_category']:
                totals['by_category'][category] = Decimal('0')
            totals['by_category'][category] += result.co2_kg
        
        if dqr_count > 0:
            totals['average_dqr'] = Decimal(dqr_sum) / Decimal(dqr_count)
        
        return totals
