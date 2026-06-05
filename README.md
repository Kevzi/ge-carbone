<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/ONNX-005C8A?style=for-the-badge&logo=onnx&logoColor=white" />
</div>

<h1 align="center">🌿 LedgerCarbon - B2B2B SaaS Carbon Engine</h1>

<p align="center">
  <strong>Transformez automatiquement les écritures comptables (FEC) en rapports carbone CSRD auditables grâce à une IA Éco-conçue.</strong>
</p>

---

## 📖 Vision & Valeur Ajoutée

**LedgerCarbon** est une plateforme SaaS (RegTech) conçue spécifiquement pour les experts-comptables. Elle leur permet de transformer le principal actif de leurs clients — le Fichier d'Écritures Comptables (FEC) — en un **bilan carbone complet, auditable et conforme à la directive européenne CSRD** (Corporate Sustainability Reporting Directive).

Notre philosophie repose sur le concept de **"Boîte de Verre" (Glass Box)** :
Contrairement aux outils d'estimation carbone classiques, LedgerCarbon calcule l'empreinte de manière déterministe en liant **chaque gramme de CO2** généré à sa ligne comptable d'origine. Cela garantit une piste d'audit parfaite pour les Commissaires aux Comptes (CAC).

## 🚀 Fonctionnalités Clés (Epics)

- 📁 **Ingestion FEC Ultra-Rapide** : Parsing streaming asynchrone validant le format A47 A-1 (LPF). Capable de traiter des fichiers de plus d'un million de lignes sans saturer la RAM.
- 🧠 **Moteur d'IA Éco-Conçue (Green AI)** : Classification automatique des libellés (NLP) via un modèle **CamemBERTv2** exécuté localement en In-Process via **ONNX Runtime (INT8)**, sans requêtes GPU externes gourmandes en énergie.
- 🏢 **Multi-Tenancy Absolue** : Isolation physique des données de chaque cabinet comptable via `django-tenants` (schémas PostgreSQL dédiés), garantissant une conformité RGPD stricte.
- 📊 **Double Matérialité** : Questionnaire interactif générant automatiquement la matrice d'Impacts, Risques et Opportunités (IRO).
- 🏭 **Sirétisation Haute Performance** : Croisement automatique avec la base SIRENE (INSEE) via l'extension `pg_trgm` de PostgreSQL.
- 📄 **Exports Réglementaires** : Génération de PDF auditables et d'exports **iXBRL / ESEF** validés par la Formula Linkbase de l'EFRAG.
- 💳 **Monétisation Intégrée** : Achat de packs de crédits via Stripe avec déduction automatique par rapport généré.

## 🛠 Stack Technique & Architecture

L'architecture est construite sur un modèle **Monolithe Modulaire** pour allier simplicité de déploiement et séparation forte des domaines métiers (DDD).

### Backend (Python/Django)
- **Framework :** Django 5 + Django REST Framework
- **Base de données :** PostgreSQL 16 (Schémas Multi-Tenants, JSONB, `pg_trgm`)
- **Asynchronisme :** Celery + Redis 7 (Queues dédiées pour l'ingestion, l'IA et l'export)
- **Intelligence Artificielle :** Modèle Transformer exporté en ONNX et quantifié en INT8 pour une inférence CPU verte et rapide.

### Frontend (React/Vite)
- **Framework :** React 18 avec TypeScript
- **Styling :** Tailwind CSS + Framer Motion (Design System Premium & Responsive)
- **State Management & Fetching :** React Query / Zustand

### Déploiement & DevOps
- **Conteneurisation :** Docker & Docker Compose
- **Tests :** Pytest (Backend) + Jest (Frontend)

## 🏗 Structure du Projet

```text
generateur-carbone/
├── src/                          # Backend Django (API)
│   ├── apps/                     # Modules métiers (Monolithe modulaire)
│   │   ├── core/                 # Gestion Multi-Tenants, Users, Stripe
│   │   ├── fec_parser/           # Upload, Streaming Parsing, Validation LPF
│   │   ├── carbon_engine/        # Moteur de règles PCG/NAF, IA ONNX, Calculs DQR
│   │   ├── report_generator/     # Génération PDF (WeasyPrint), Matrice IRO, Export iXBRL
│   │   └── credits/              # Déduction des crédits, Historique
│   ├── ledgercarbon/             # Configuration principale Django (Settings, Celery)
│   ├── models/                   # Modèles IA (ONNX INT8, vocabulaire)
│   └── scripts/                  # Scripts de Machine Learning et utilitaires
├── frontend/                     # Application React (Vite)
│   └── src/
│       ├── components/           # Composants UI partagés
│       ├── features/             # Domaines métiers Frontend
│       └── pages/                # Vues principales (Dashboard, Drill-down)
└── docker-compose.yml            # Services d'infrastructure (PostgreSQL, Redis)
```

## ⚡ Démarrage Rapide (Environnement de Dév)

### 1. Démarrer l'infrastructure (Docker)
```bash
docker compose up -d
```
*Cela lance PostgreSQL et Redis sur leurs ports standards.*

### 2. Configurer le Backend
```bash
cd src
python -m venv venv

# Activation (Windows)
.\venv\Scripts\Activate.ps1
# Activation (Mac/Linux)
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Initialisation des bases de données (Multi-Tenant)
python manage.py migrate_schemas --shared
python manage.py migrate

# Entraînement et génération du modèle d'IA (Optionnel si vous l'avez déjà)
python scripts/train_nlp_model.py
```

### 3. Configurer le Frontend
```bash
cd ../frontend
npm install
npm run dev
```

## 🧪 Tests & Qualité

Pour lancer la suite de tests automatisés (Backend) :
```bash
cd src
pytest
```
*Note : Le fichier `test_fec_2024.txt` est inclus pour tester l'ingestion localement.*

## 🔒 Sécurité et Conformité
- **Data Privacy :** Les fichiers FEC uploadés sont stockés de manière éphémère et supprimés **immédiatement** après leur parsing en base de données.
- **Isolation :** Un schéma de base de données = Un cabinet comptable. Impossible de croiser les données entre clients.
- **Traçabilité :** Le `DQR` (Data Quality Ratio) est stocké immuablement pour chaque ligne comptable.

---
*Ce projet est géré selon la méthodologie BMad (Behavioral Multi-Agent Development).*
