import os
import random
import csv
from datetime import datetime, timedelta

def main():
    output_file = os.path.join(os.path.dirname(__file__), "..", "models", "fec_synthetic_dataset.csv")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 18 colonnes obligatoires (LPF A47 A-1)
    columns = [
        "JournalCode", "JournalLib", "EcritureNum", "EcritureDate", "CompteNum", 
        "CompteLib", "CompAuxNum", "CompAuxLib", "PieceRef", "PieceDate", 
        "EcritureLib", "Debit", "Credit", "EcritureLet", "DateLet", "ValidDate", 
        "Montantdevise", "Idevise", "CategorieADEME"
    ]
    
    # Base Sirene Simulée avec catégories ADEME associées
    fournisseurs_ademe = [
        # Energie
        {"nom": "EDF Pro", "ademe": "Energie", "compte": "606100", "prefix": ["Fact. EDF", "Prélèvement EDF", "Energie mois", "Abo EDF", "Facture Electricite"]},
        {"nom": "TotalEnergies", "ademe": "Energie", "compte": "606100", "prefix": ["Facture Gaz", "Total", "Prelevement TotalEnergies", "Abo Gaz"]},
        {"nom": "Engie", "ademe": "Energie", "compte": "606100", "prefix": ["Engie facture", "Gaz Engie", "Elec Engie"]},
        
        # Déplacements
        {"nom": "SNCF", "ademe": "Déplacements", "compte": "625100", "prefix": ["Billet SNCF", "TGV Inoui", "Train Paris", "SNCF Voyage", "Fact. SNCF", "sncf"]},
        {"nom": "Air France", "ademe": "Déplacements", "compte": "625100", "prefix": ["Vol AF", "Billet Avion", "Air France vol", "Deplacement avion"]},
        {"nom": "Total", "ademe": "Déplacements", "compte": "606220", "prefix": ["Carburant", "Essence", "Gasoil", "Plein Total", "Station Service", "Péage"]},
        {"nom": "Vinci Autoroutes", "ademe": "Déplacements", "compte": "625100", "prefix": ["Peage", "Autoroute", "Badge Telepeage Vinci"]},
        
        # Achats de Biens (Matériel)
        {"nom": "Dell France", "ademe": "Achats de Biens", "compte": "218300", "prefix": ["Achat PC", "Dell XPS", "Ordi Dell", "Materiel Info", "Facture DELL"]},
        {"nom": "Apple", "ademe": "Achats de Biens", "compte": "218300", "prefix": ["Macbook", "Apple Store", "Iphone", "Materiel Apple"]},
        {"nom": "Boulanger", "ademe": "Achats de Biens", "compte": "606400", "prefix": ["Fournitures", "Achats Boulanger", "Ecran PC", "Clavier Souris"]},
        {"nom": "Bureau Vallee", "ademe": "Achats de Biens", "compte": "606400", "prefix": ["Papeterie", "Fournitures bureau", "Ramette papier", "Bureau Vallee"]},
        
        # Achats de Services
        {"nom": "OVH Cloud", "ademe": "Achats de Services", "compte": "626000", "prefix": ["Abo OVH", "Hebergement web", "Serveur OVH", "Facture cloud", "OVH"]},
        {"nom": "Amazon Web Services", "ademe": "Achats de Services", "compte": "626000", "prefix": ["AWS", "Abo AWS", "Serveurs Amazon", "Cloud AWS"]},
        {"nom": "Orange Pro", "ademe": "Achats de Services", "compte": "626000", "prefix": ["Forfait Mobile", "Abo Internet", "Orange Fibre", "Telephonie"]},
        {"nom": "KPMG", "ademe": "Achats de Services", "compte": "622600", "prefix": ["Honoraires CAC", "Facture KPMG", "Audit", "Prestation Conseil"]},
        {"nom": "Malt", "ademe": "Achats de Services", "compte": "622600", "prefix": ["Prestation Freelance", "Malt Developpeur", "Malt Fact."]},
    ]
    
    bruit_mots = ["janvier", "fev", "mars", "T1", "T2", "2024", "ref", "n°", "client", "cb", "prelev", "virement", "reglement"]
    defauts = ["", " - ", " _ ", " / ", "  "]
    
    num_lignes = 10000
    start_date = datetime(2024, 1, 1)
    
    print(f"Generating {num_lignes} synthetic rows...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        writer.writerow(columns)
        
        for i in range(1, num_lignes + 1):
            fournisseur = random.choice(fournisseurs_ademe)
            
            # Dates
            ecr_date = start_date + timedelta(days=random.randint(0, 360))
            ecr_date_str = ecr_date.strftime("%Y%m%d")
            
            # Libellé génératif (Bruit LLM simulé)
            prefix = random.choice(fournisseur["prefix"])
            bruit = random.choice(bruit_mots) if random.random() > 0.5 else ""
            defaut = random.choice(defauts)
            
            # 10% chance de tout mettre en majuscule, 10% minuscule
            libelle = f"{prefix}{defaut}{bruit}".strip()
            case_rand = random.random()
            if case_rand < 0.1:
                libelle = libelle.upper()
            elif case_rand < 0.2:
                libelle = libelle.lower()
                
            # 2% chance de faute de frappe
            if random.random() < 0.02 and len(libelle) > 5:
                idx = random.randint(0, len(libelle)-1)
                libelle = libelle[:idx] + libelle[idx+1:]
                
            debit = round(random.uniform(10.0, 5000.0), 2)
            
            row = [
                "AC", "Achats", f"AC{i:05d}", ecr_date_str, fournisseur["compte"], 
                "Fournisseurs", f"FOU{random.randint(1,999):03d}", fournisseur["nom"], 
                f"FA-{ecr_date.strftime('%y%m')}-{i:04d}", ecr_date_str, 
                libelle, f"{debit}".replace('.', ','), "0,00", "", "", ecr_date_str, "0,00", "", 
                fournisseur["ademe"]
            ]
            writer.writerow(row)
            
    print(f"Dataset generated at {output_file}")

if __name__ == "__main__":
    main()
