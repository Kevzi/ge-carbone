import pandas as pd

def extract_accounting_leads(parquet_file_path, output_csv_path):
    print("Chargement de la base Sirene (cela peut prendre quelques secondes)...")
    
    # 1. Lecture du fichier Parquet
    df = pd.read_parquet(parquet_file_path)
    
    # 2. Filtrage des entreprises actives uniquement (Etat Administratif = 'A')
    df_actifs = df[df['etatAdministratifUniteLegale'] == 'A']
    
    # 3. Filtrage sur le code NAF de l'expertise comptable (69.20Z)
    df_comptables = df_actifs[df_actifs['activitePrincipaleUniteLegale'] == '69.20Z']
    
    # 4. Filtrage sur la tranche d'effectif (Le "Hungry Middle")
    # 12 = 20 à 49 salariés | 21 = 50 à 99 salariés | 22 = 100 à 199 salariés
    tranches_cibles = ['12', '21', '22']
    df_cibles = df_comptables[df_comptables['trancheEffectifsUniteLegale'].isin(tranches_cibles)]
    
    # 5. Sélection et renommage des colonnes utiles pour la prospection
    colonnes_a_garder = [
        'siren', 
        'denominationUniteLegale', 
        'trancheEffectifsUniteLegale',
        'categorieJuridiqueUniteLegale'
    ]
    df_final = df_cibles[colonnes_a_garder].copy()
    
    # Remplacement des codes de tranches par du texte lisible
    mapping_tranches = {
        '12': '20 à 49 salariés',
        '21': '50 à 99 salariés',
        '22': '100 à 199 salariés'
    }
    df_final['trancheEffectifsUniteLegale'] = df_final['trancheEffectifsUniteLegale'].map(mapping_tranches)
    
    # 6. Exportation du fichier de prospection
    df_final.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"Extraction terminée ! {len(df_final)} cabinets trouvés et sauvegardés dans {output_csv_path}.")

if __name__ == "__main__":
    FICHIER_SOURCE = "stock-stockunitelegale-parquet.parquet" 
    FICHIER_RESULTAT = "leads_cabinets_comptables.csv"
    
    extract_accounting_leads(FICHIER_SOURCE, FICHIER_RESULTAT)
