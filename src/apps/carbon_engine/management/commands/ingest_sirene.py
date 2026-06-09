import os
import pandas as pd
from django.core.management.base import BaseCommand
from apps.carbon_engine.models import SireneStock

class Command(BaseCommand):
    help = "Ingest Sirene data from a Parquet file using pyarrow and pandas"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Parquet file')
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10000,
            help='Batch size for reading and bulk_create (default: 10000)'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        batch_size = options['batch_size']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File {file_path} not found."))
            return

        self.stdout.write(self.style.SUCCESS(f"Reading {file_path} in chunks of {batch_size}..."))
        
        try:
            import pyarrow.parquet as pq
            
            parquet_file = pq.ParquetFile(file_path)
            
            total_rows = parquet_file.metadata.num_rows
            self.stdout.write(f"Total rows to process: {total_rows}")
            
            processed = 0
            
            # Read in batches
            for batch in parquet_file.iter_batches(batch_size=batch_size):
                df = batch.to_pandas()
                
                # Check for standard Insee column names
                col_siren = 'siren' if 'siren' in df.columns else df.columns[0]
                
                col_denom = 'denominationUniteLegale'
                if col_denom not in df.columns:
                    col_denom = 'nomUniteLegale' if 'nomUniteLegale' in df.columns else 'denomination'
                    if col_denom not in df.columns:
                        col_denom = 'enseigne1Etablissement' if 'enseigne1Etablissement' in df.columns else df.columns[1]

                col_naf = 'activitePrincipaleUniteLegale'
                if col_naf not in df.columns:
                    col_naf = 'activitePrincipaleEtablissement' if 'activitePrincipaleEtablissement' in df.columns else 'naf'
                    if col_naf not in df.columns:
                        col_naf = df.columns[2]

                col_naf25_etab = 'activitePrincipaleNAF25Etablissement'
                col_naf25_ul = 'activitePrincipaleNAF25UniteLegale'
                has_naf25_etab = col_naf25_etab in df.columns
                has_naf25_ul = col_naf25_ul in df.columns
                
                # Filter out rows with missing vital data
                df = df.dropna(subset=[col_siren, col_denom, col_naf])
                
                instances = []
                for _, row in df.iterrows():
                    siren = str(row[col_siren])[:9]
                    denom = str(row[col_denom])[:255]
                    
                    naf25_etab = None
                    if has_naf25_etab and pd.notna(row[col_naf25_etab]):
                        val = str(row[col_naf25_etab]).strip()
                        if val.lower() not in ('nan', 'none', '<na>', 'nat', ''):
                            naf25_etab = val.replace('.', '')[:6]
                        
                    naf25_ul = None
                    if has_naf25_ul and pd.notna(row[col_naf25_ul]):
                        val = str(row[col_naf25_ul]).strip()
                        if val.lower() not in ('nan', 'none', '<na>', 'nat', ''):
                            naf25_ul = val.replace('.', '')[:6]
                    
                    instances.append(
                        SireneStock(
                            siren=siren,
                            denomination=denom,
                            naf_code=str(row[col_naf]).replace('.', '')[:5],
                            naf_2025_etablissement=naf25_etab,
                            naf_2025_unite_legale=naf25_ul
                        )
                    )
                
                SireneStock.objects.bulk_create(instances, batch_size=batch_size, ignore_conflicts=True)
                
                processed += len(instances)
                if processed % (batch_size * 10) == 0:
                    self.stdout.write(f"Processed {processed}/{total_rows} rows")
                
            self.stdout.write(self.style.SUCCESS(f"Ingestion completed successfully. Total processed: {processed}"))
            
        except ImportError:
            self.stderr.write(self.style.ERROR("pyarrow is required to read parquet files. Run pip install pyarrow."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during ingestion: {e}"))
