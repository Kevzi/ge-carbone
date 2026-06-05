import logging
from celery import shared_task
from django_tenants.utils import schema_context
from .models import CarbonEntry, EmissionFactor
from .services.nlp_service import NLPService

logger = logging.getLogger(__name__)

@shared_task(queue='nlp_tasks')
def enrich_fec_nlp_task(report_id, schema_name):
    """
    Celery task to enrich CarbonEntry records with NLP predictions.
    Runs in the 'nlp_tasks' queue.
    """
    with schema_context(schema_name):
        # Fetch entries that need NLP enrichment
        entries = CarbonEntry.objects.filter(report_id=report_id).exclude(mapping_method='nlp')
        
        if not entries.exists():
            logger.info(f"No entries to enrich for report {report_id} in {schema_name}.")
            return 0
            
        nlp_service = NLPService()
        
        batch_size = 1000
        total_enriched = 0
        
        # Optimization: Pre-fetch emission factors to avoid N+1 queries
        factors = list(EmissionFactor.objects.all())
        factors_by_category = {f.category: f for f in factors if f.category}
        
        # Optimization: Use iterator and manual chunking to avoid OOM
        iterator = entries.iterator(chunk_size=batch_size)
        
        import itertools
        while True:
            batch = list(itertools.islice(iterator, batch_size))
            if not batch:
                break
                
            texts = [entry.ecriture_lib for entry in batch]
            
            categories = nlp_service.predict_category(texts)
            
            updates = []
            for entry, category in zip(batch, categories):
                if category:
                    # Find matching emission factor without querying DB
                    factor = factors_by_category.get(category)
                    
                    entry.mapping_method = 'nlp'
                    entry.dqr = 4
                    if factor:
                        entry.emission_factor = factor
                    
                    updates.append(entry)
            
            if updates:
                CarbonEntry.objects.bulk_update(updates, ['mapping_method', 'dqr', 'emission_factor'])
                total_enriched += len(updates)
                
        logger.info(f"Successfully enriched {total_enriched} entries for report {report_id}.")
        return total_enriched
