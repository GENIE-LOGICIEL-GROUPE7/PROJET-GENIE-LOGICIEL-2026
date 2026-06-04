# PROJET-GENIE-LOGICIEL-2026
Depot pour le projet de genie logciel groupe7
## 📁 Guide de lecture du Code (Python) situe dans le codes pyhcharm dans pyhcharmMisc

Pour consulter la logique métier et les scripts Python de ce projet, veuillez vous référer aux dossiers suivants :

### 1. Logique de l'Application (Le cœur du projet)
Le dossier `resto_groupe7 finale/restaurant/` contient l'essentiel de l'implémentation :
- **`models.py`** : Définition des tables MySQL les 7 modules  que on a implementer .
- **`views.py`** : Contient les fonctions  qui traitent les requêtes.
- **`urls.py`** : Définit les routes internes de l'application.

### 2. Configuration du Projet
Le dossier `resto_groupe7/` contient les réglages globaux :
- **`settings.py`** : Configuration de la base de données MySQL et des paramètres Django.
- **`urls.py`** : Le point d'entrée principal avec l'aiguillage .

### 3. Interface (Templates)
- Le dossier `restaurant/templates` contient les fichiers `.html` qui font le lien entre le Python et l'affichage.
- 
### 4. Pour lancer le code python
- lancer dans la base de donne 'Restaurant' avec mysql dans le dossier base de donne sql restaurant
- Assurer vous d'avoir prealablement installe dganjo dans pycharm ou IDE de votre choix
 -Puis aller dans pyhcharm  connecte votre base de donne restaurant avec vous identifiant personnel de sql a django dans settings.py( line 78 l'operation pour faire cela est detaille dans le rapport)
  -Maintenant puisque le code est deja la tape juste ces commande sur le terminal python
      python manage.py makemigrations
      python manage.py migrate
  -Puis ton compte admin avec le code python :'manage.py createsuperuser' puis les information qui suis
  -Maintenant tape le code: ' python manage.py runserver ' puis clique sur le premier lien apres vous serez rediriger vers l'application avec juste 2 module implemente
