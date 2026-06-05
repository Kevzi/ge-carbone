# LedgerCarbon Backend

## Description
Plateforme SaaS B2B2B de transformation FEC → Rapport CSRD auditable.

## Stack
- Python 3.11+
- Django 5.x + DRF
- PostgreSQL 16
- Redis 7.x
- Celery 5.x

## Setup Development

```bash
# 1. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer les variables d'environnement
copy .env.example .env
# Éditer .env avec vos valeurs

# 4. Lancer les services (Docker)
docker-compose up -d postgres redis

# 5. Appliquer les migrations
python manage.py migrate

# 6. Créer un superuser
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

## Structure du projet

```
src/
├── ledgercarbon/          # Projet Django principal
│   ├── settings/          # Configuration par environnement
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/              # Modèles de base (Cabinet, User)
│   ├── fec_parser/        # Ingestion et validation FEC
│   ├── carbon_engine/     # Mapping PCG → ADEME, calcul CO2
│   ├── report_generator/  # Génération PDF + audit trail
│   └── credits/           # Système de crédits Stripe
├── manage.py
└── requirements.txt
```

## API Documentation

Une fois le serveur lancé: http://localhost:8000/api/docs/

## Tests

```bash
pytest
```

## License

Propriétaire - LedgerCarbon
