<div align="center">
  <img src="https://img.shields.io/badge/Status-En%20Développement-orange?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />

  <br />
  <br />

  <h1><img src="frontend/src/assets/logo.png" width="40" height="40" style="vertical-align: middle; margin-right: 10px;" /> LedgerCarbon</h1>
  
  <p>
    <strong>Une solution automatisée permettant aux cabinets d'expertise comptable de générer les bilans carbones de leurs clients à partir du Fichier des Écritures Comptables (FEC).</strong>
  </p>
</div>

---

## 📖 Sommaire
- [À propos du projet](#-à-propos-du-projet)
- [Architecture du Système](#-architecture-du-système)
- [Modèle Multi-Tenant (Isolation des données)](#-modèle-multi-tenant-isolation-des-données)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Stack Technique](#-stack-technique)
- [Guide d'Installation](#-guide-dinstallation)

---

## 🎯 À propos du projet

Le **Générateur Carbone** transforme la comptabilité classique en comptabilité carbone. Conçu spécifiquement pour les experts-comptables, il automatise l'analyse des Fichiers d'Écritures Comptables (FEC), la catégorisation des achats, et leur conversion en équivalent CO₂ (Scope 1, 2 et 3) via la base Empreinte® de l'ADEME.

---

## 🏗 Architecture du Système

Le projet est divisé en deux parties majeures communiquant via une API REST. Le moteur de calcul carbone (`carbon_engine`) traite les lignes comptables, tandis que le parseur (`fec_parser`) ingère et normalise les fichiers.

```mermaid
flowchart TD
    %% Styling
    classDef client fill:#1E293B,stroke:#475569,color:#fff,stroke-width:2px,rx:8px
    classDef backend fill:#0369A1,stroke:#0284C7,color:#fff,stroke-width:2px,rx:8px
    classDef db fill:#166534,stroke:#15803D,color:#fff,stroke-width:2px,rx:8px

    Client[💻 Navigateur Web / React SPA]:::client
    
    Client ===>|Appels REST API| Gateway
    
    subgraph Backend [⚙️ Backend Django]
        direction TB
        Gateway(API Gateway / DRF):::backend ==> Auth[🔐 Module Auth & Tenants]:::backend
        Auth ==> FEC[📄 Parseur FEC]:::backend
        Auth ==> Report[📊 Générateur de Rapports]:::backend
        
        FEC -.->|Normalisation| Engine[⚡ Moteur Carbone]:::backend
        Report -.-> Engine
        Report -.-> Materiality[📋 Évaluation Double Matérialité]:::backend
    end

    subgraph DB [🗄️ Bases de données PostgreSQL]
        direction LR
        TenantSchema[(Schema Tenant : Cabinet A)]:::db
        PublicSchema[(Schema Public : ADEME)]:::db
    end

    %% Connections Backend <-> DB
    Auth -.->|Routage| TenantSchema
    FEC <==>|Données isolées| TenantSchema
    Report <==>|Bilan & Piste d'audit| TenantSchema
    Engine ===>|Lecture Facteurs Émission| PublicSchema
```

---

## 🔐 Modèle Multi-Tenant (Isolation des données)

La sécurité et la confidentialité financière sont au cœur de l'application. L'architecture s'appuie sur le concept de **Multi-Tenancy par schémas PostgreSQL** via `django-tenants`.

- **Schema Public (`public`)** : Contient les données partagées par tous. 
  - *Exemples : Méta-données des cabinets, Facteurs d'émissions de l'ADEME, Déflateurs INSEE.*
- **Schemas Locataires (`cabinet_a`, `cabinet_b`)** : Chaque cabinet possède son propre schéma isolé au niveau de la base de données.
  - *Exemples : Fichiers FEC clients, Lignes comptables, Pistes d'audit, Évaluations IRO.*

```mermaid
erDiagram
    PUBLIC_SCHEMA ||--o{ TENANT_SCHEMA_1 : contient
    PUBLIC_SCHEMA ||--o{ TENANT_SCHEMA_2 : contient
    
    PUBLIC_SCHEMA {
        Cabinet tenant
        EmissionFactor base_ademe
        Deflator insee
    }
    
    TENANT_SCHEMA_1 {
        Report client_a_2023
        CarbonEntry achats
        MaterialityAssessment iro
    }
```

---

## ✨ Fonctionnalités Principales

1. **Upload & Parsing FEC** : Ingestion normalisée des écritures comptables (txt, csv) avec validation des colonnes obligatoires.
2. **Sirétisation Avancée (Open Data)** : Enrichissement des données via le fichier "StockEtablissement" de l'INSEE au format **Apache Parquet**, interrogé en mémoire via *Polars* pour des performances fulgurantes.
3. **Moteur de Calcul CO₂ (Ratio Monétaire & Physique)** : 
   - Application des ratios monétaires de la Base Carbone ajustés de l'inflation via les **déflateurs INSEE** (mise à jour mensuelle automatique).
   - Possibilité de correction via des unités physiques pour une précision maximale.
4. **Intelligence Artificielle (Green AI)** : Désambiguïsation NLP basée sur le modèle **DeBERTaV3** (`almanach/camembertav2-base`) assurant un matching sémantique robuste. Le modèle s'enrichit via une **boucle de feedback** stricte et **anonymisée (RGPD)**.
5. **Conformité CSRD & Export XBRL** :
   - Évaluation de la Double Matérialité (IRO) intégrée.
   - Piste d'Audit Fiable historisée pour les Commissaires aux Comptes (CAC).
   - Génération du bilan au format **iXBRL** (norme ESEF / taxonomie EFRAG) validé par le moteur open-source *Arelle*. Afin de garantir la minimisation des données (RGPD), les livrables iXBRL et PDF sont automatiquement purgés après 24h.

---

### 🧠 Comment fonctionne notre moteur IA ?

Le moteur IA (Green AI) a pour but de faire le lien entre une écriture comptable brute (souvent très laconique) et le Facteur d'Émission correspondant dans la base ADEME.
Pour cela, il utilise un modèle d'embedding (DeBERTaV3) afin d'évaluer la proximité sémantique et attribue un score de confiance. Si l'humain corrige la prédiction (par exemple via le Dashboard Top Émetteurs), cette correction vient enrichir le système via une boucle d'apprentissage continu.

```mermaid
flowchart TD
    %% Styling
    classDef input fill:#F3F4F6,stroke:#D1D5DB,color:#111827,stroke-width:2px,rx:8px
    classDef ai fill:#6366F1,stroke:#4338CA,color:#fff,stroke-width:2px,rx:8px
    classDef db fill:#166534,stroke:#15803D,color:#fff,stroke-width:2px,rx:8px
    classDef human fill:#F59E0B,stroke:#D97706,color:#fff,stroke-width:2px,rx:8px

    subgraph Phase 1 : Ingestion
        A[Ligne FEC<br>Compte: 6061<br>Libellé: 'Achat fourniture EDF']:::input
        A --> B[Normalisation NLP<br>Nettoyage du texte]:::input
    end

    subgraph Phase 2 : Moteur de Prédiction
        B --> C{Recherche Vectorielle<br>DeBERTaV3 Embeddings}:::ai
        C <--> DB[(Base ADEME<br>Facteurs d'Émissions)]:::db
        C --> D[Top 3 Prédictions avec<br>Score de Confiance %]:::ai
        D --> E[Sélection automatique<br>du Facteur d'Émission]:::ai
    end

    subgraph Phase 3 : Human in the loop & Apprentissage
        E --> F[Validation par l'Auditeur<br>Dashboard Top Émetteurs]:::human
        F -- "Si l'auditeur corrige" --> G[Enregistrement de la correction<br>dans la mémoire du tenant]:::db
        G --> C
        F -- "Si l'auditeur valide" --> H[Bilan Carbone & Piste d'Audit]:::input
    end
```

---

## 💻 Stack Technique

### Backend (API)
- **Framework:** Django 5.x, Django REST Framework
- **Base de données:** PostgreSQL (avec support JSONB et Trigramme)
- **Multi-Tenancy:** django-tenants
- **Tests:** Pytest
- **Traitement de données:** Pandas / NumPy (pour l'analyse de gros fichiers FEC)

### Frontend (SPA)
- **Framework:** React 18, TypeScript, Vite
- **Routage:** React Router DOM
- **Design & UI:** Tailwind CSS, Recharts (pour la data visualisation)
- **Gestion d'état & Fetch:** Hooks natifs & API Fetch customisée avec rafraichissement de tokens JWT.

---

## 🚀 Guide d'Installation

### 1. Prérequis
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (L'extension `pg_trgm` doit être activée)

### 2. Installation Backend
```bash
cd src
# Création de l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/Mac

# Installation des dépendances
pip install -r requirements.txt

# Création des schémas et migrations
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# Lancement du serveur de développement
python manage.py runserver
```

### 3. Installation Frontend
```bash
cd frontend

# Installation des paquets npm
npm install

# Lancement du serveur Vite
npm run dev
```

L'application sera accessible sur `http://localhost:5173`. L'API écoute sur `http://localhost:8000/api/v1/`.

---

<div align="center">
  <i>Développé avec ❤️ pour la transition écologique.</i>
</div>
