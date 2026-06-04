# Restaurant Management System (RMS)
## Groupe 7 — GTEL 3046 — ENSPY 2025-2026

### Structure des fichiers fournis
```
restaurant/
├── models.py          ← 12 modèles (7 modules fonctionnels)
├── views.py           ← Toutes les vues avec logique métier
├── urls.py            ← Configuration du routage
├── admin.py           ← Interface d'administration Django
├── forms.py           ← Formulaires validés
├── signals.py         ← Signaux (notifications cuisine)
├── apps.py            ← Configuration de l'application
├── settings.py        ← Configuration complète Django/MySQL
└── templates/
    ├── base.html             ← Template de base Bootstrap 5
    └── dashboard/
        └── index.html        ← Tableau de bord avec Chart.js
```

### Installation
```bash
# 1. Créer et activer l'environnement
conda create -n resto_env7 python=3.10
conda activate resto_env7

# 2. Installer les dépendances
pip install django pymysql Pillow django-crispy-forms crispy-bootstrap5

# 3. Créer le projet
django-admin startproject resto_groupe7 .
python manage.py startapp restaurant

# 4. Copier les fichiers fournis dans restaurant/
# IMPORTANT : Copier settings.py dans resto_groupe7/

# 5. Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE Restaurant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 6. Migrations
python manage.py makemigrations restaurant
python manage.py migrate

# 7. Super-utilisateur
python manage.py createsuperuser
# Username: TONLEU_RAMSES

# 8. Lancer
python manage.py runserver
# → http://127.0.0.1:8000/
# → http://127.0.0.1:8000/admin/
# → http://127.0.0.1:8000/dashboard/
```

### Modules implémentés
| # | Module | Fichier(s) | Statut |
|---|--------|-----------|--------|
| 1 | Authentification & Users | models.py, views.py, forms.py | ✅ Complet |
| 2 | Gestion des Recettes | models.py, views.py | ✅ Complet |
| 3 | Gestion des Produits | models.py, views.py, forms.py | ✅ Complet |
| 4 | Gestion des Commandes | models.py, views.py, forms.py | ✅ Complet |
| 5 | Gestion du Stock | models.py, views.py, forms.py | ✅ Complet |
| 6 | Gestion RH | models.py, views.py | ✅ Complet |
| 7 | Dashboard & Revenue | models.py, views.py, templates | ✅ Complet |

### URLs disponibles
- `/` ou `/menu/`     → Carte des plats (public)
- `/login/`           → Connexion
- `/dashboard/`       → Tableau de bord (Director/Admin)
- `/orders/create/`   → Prise de commande (Server)
- `/kitchen/`         → Interface cuisine (Cook/Head Chef)
- `/stock/`           → Gestion des stocks (Stock Manager)
- `/products/`        → Catalogue produits (Admin/Head Chef)
- `/hr/`              → Gestion RH (Admin)
- `/admin/`           → Panneau d'administration Django
