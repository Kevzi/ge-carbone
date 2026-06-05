<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
</div>

<h1 align="center">🌿 LedgerCarbon - B2B2B SaaS Carbon Engine</h1>

<p align="center">
  <strong>Transformez automatiquement les écritures comptables (FEC) en rapports carbone CSRD auditables.</strong>
</p>

---

## 📖 À propos du projet

**LedgerCarbon** est une plateforme SaaS B2B2B moderne conçue pour les cabinets comptables. Elle leur permet de proposer une nouvelle mission RSE à leurs clients (PME/ETI) en transformant de manière automatisée leurs Fichiers d'Écritures Comptables (FEC) en bilans carbone certifiés, compatibles avec les exigences de la norme européenne **CSRD**.

Grâce à une approche **Ledger-First** et une architecture "Boîte de Verre", LedgerCarbon remonte la chaîne de valeur du CO2 jusqu'à la ligne comptable exacte, fournissant une traçabilité indispensable pour l'auditabilité financière.

## 🚀 Fonctionnalités Clés

- 📁 **Ingestion FEC Ultra-Rapide** : Analyse et validation syntaxique strict des fichiers FEC (conformément à l'Article A47 A-1 du LPF).
- 🧠 **Moteur de Mapping Carbone Intelligent** : Classification automatique (PCG → ADEME) avec traitement du langage naturel (NLP) sur les libellés pour une précision accrue (Score DQR).
- 🔍 **Piste d'Audit "Boîte de Verre"** : Traçabilité totale ("Drill-down") depuis le scope d'émission de CO2 jusqu'à la ligne comptable source.
- 🏢 **Architecture Multi-Tenant** : Isolation totale des données par cabinet grâce à `django-tenants` (utilisation de schémas PostgreSQL distincts).
- 💳 **Système de Crédits (SaaS)** : Paiement à l'usage via intégration Stripe avec facturation et quotas par cabinet.
- 📄 **Exports Auditables** : Génération de bilans carbone interactifs et export PDF.

## 🛠 Stack Technique

Ce projet est développé selon les standards de l'industrie pour assurer performance, sécurité et scalabilité :

### Backend (API REST)
- **Python 3.11** / **Django 5** / **Django REST Framework**
- **PostgreSQL 16** avec **Django-Tenants** pour le multi-tenant as-a-service.
- **Celery & Redis 7** pour le traitement asynchrone des fichiers volumineux.
- Tests automatisés exécutés sous **Pytest** (`pytest-django`).

### Frontend (SPA)
- **React 18** avec **TypeScript**
- **Vite** pour un build ultrarapide
- **Tailwind CSS** & **Framer Motion** pour une UI/UX dynamique et premium
- Authentification par **JWT** (JSON Web Tokens)
- Routage avec **React Router v6**

## 🏗 Architecture du Moteur

LedgerCarbon repose sur trois services majeurs intégrés au backend :
1. **FEC Validator & Parser** : Un parseur par flux (`stream parser`) pour lire efficacement les fichiers pesant plusieurs centaines de Mo sans engorger la RAM.
2. **PCG Mapping Service** : Combine un système hiérarchique exact, préfixal et algorithmique (mots-clés NLP) pour associer la bonne catégorie de la Base Empreinte ADEME.
3. **Carbon Calculator** : Pondération des montants débiteurs nets aux facteurs d'émissions pour générer les rapports (Scope 1, 2, 3).

## ⚡ Démarrage Rapide (Quickstart)

### Prérequis
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+

### Lancement via Docker (Recommandé)

1. Clonez le dépôt et démarrez les bases de données (PostgreSQL et Redis) via Docker :
```bash
cd src
docker compose up -d
```

2. Initialisez l'environnement Backend :
```bash
cd src
python -m venv venv
# Windows : .\venv\Scripts\Activate.ps1
# Mac/Linux : source venv/bin/activate
pip install -r requirements.txt

# Création de la base publique (Multi-tenant)
python manage.py migrate_schemas --shared
python manage.py migrate
```

3. Exécutez les tests pour valider l'installation :
```bash
pytest
```

4. Lancez le Frontend :
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Fichier de Test

Un fichier `test_fec_2024.txt` est inclus à la racine du projet pour simuler un apport de données comptables. Un workflow de test est également disponible pour exécuter le moteur directement en ligne de commande :

```bash
python src/test_workflow.py
```

## 🔐 Sécurité & RGPD
- Isolation stricte des locataires (Tenants).
- Mots de passe hashés avec PBKDF2, JWT tokens avec expiration courte et rafraîchissement.
- Suppression automatisée des fichiers FEC une fois parsés.

---
*Ce projet fait partie de mon portfolio professionnel et démontre mes compétences en conception d'architecture SaaS, développement Backend complexe (Django/PostgreSQL/Multi-tenant) et création d'interfaces Frontend réactives.*
