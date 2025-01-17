# FightPredixScraping

<p align="center">
  <img src="../../FightPredixApp/img/logo_readme.png" alt="Logo de mon projet" width="200" height="200">
</p>

## Quelques informations

- La collecte des données a été réalisée à l'aide des modules `Selenium`, `BeautifulSoup` et `rapidfuzz` :

  - `Selenium` a été utilisé pour automatiser la navigation sur les sites web et extraire les données dynamiques.
  - `BeautifulSoup` a permis de parser et d'extraire les informations pertinentes des pages HTML.
  - `rapidfuzz` a été employé pour effectuer des correspondances floues et améliorer la précision des données collectées.

### UFC.com

Pour accéder aux scripts de scraping des combattants sur [ufc.com](https://www.ufc.com/), rendez-vous sur :

  - `lib_front_page_ufc.py`
  - `lib_page_combattant_ufc.py`

Cette partie du processus a permis la récupération de la quasi-totalité des combattants actuels et retirés de l'**UFC**. Parmi les données récoltées, vous retrouverez leurs noms et surnoms, leur statut (actif ou non), leur nombre de victoires/défaites, leur style de combat et plusieurs de leurs statistiques actuelles comme la **Précision Saisissante** (Significant Strike en anglais).

Cette procédure s'effectue en deux temps :

1. Dans un premier temps, elle ouvre un **driver** sur la page ufc.com récapitulant chaque combattant.
2. Puis un autre driver explore la page de chaque combattant pour récupérer les informations.

### UFC stats

Sur [ufc stats](http://www.ufcstats.com/statistics/events/completed), nous avons récupéré des données sur la quasi-totalité des combats ayant eu lieu à l'**UFC**. Parmi les données récoltées, nous avons :

- Les combattants et le vainqueur du combat.
- Les statistiques des combattants au cours du combat.

Nous avons également récupéré des statistiques additionnelles sur les combattants. **Les statistiques de combats utilisées pour construire nos modèles sont issues de cette partie de la collecte des données**. Pour accéder aux scripts :

- `lib_combats.py`
- `lib_ufc_stats.py`

Sur la page Events de ufc stats, la quasi-totalité des événements est répertoriée. Le script explore chaque combat composant chaque événement et récupère les statistiques issues de chaque combat.

En ce qui concerne les données additionnelles sur les combattants, `rapidfuzz` a permis de résoudre le problème de différentiation des noms sur chaque site.

### Tapology

**Attention : Cette partie de la collecte des données n'est réalisable que si vous disposez de NordVPN. Sinon, utilisez le script actuel qui se sert du fichier `final_tapology.json`. Nous nous efforcerons de tenir ce fichier à jour.**

D'autres informations comme leurs pays de résidence/naissance ont été récupérées sur [Tapology](https://www.tapology.com/) :

- `lib_scraping_tapology.py`
- `lib_nettoyage_tapology.py`
- `lib_join_ufc_tapology.py`

La procédure est similaire à ufc stats, mais le script redémarre un nouveau driver avec une nouvelle adresse IP à chaque bannissement de l'adresse IP.

Ce script pourrait subir des changements prochainement car il ne contient pas l'utilisation de `rapidfuzz` et se sert d'un dictionnaire pour corriger les éventuelles erreurs dues à la différentiation des noms.

### UFC fans

Cette partie de la collecte des données se concentre sur les arbitres des combats :

- `lib_arbitre.py`

## Prérequis

- Python 3.13

## Fonctionnalités

- Module entièrement documenté pour les interfaces publiques et privées.
- Formatage du code avec `Black` pour respecter les normes de PEP 8.
- Gestion des dépendances avec `uv`.
- Vérification des types avec `Mypy`.
- Tests unitaires et d'intégration avec `Pytest`, et couverture de tests avec `Pytest-cov`.

## Contributeurs

- [Gregory Jaillet](https://github.com/Greg-jllt)
- [Hugo Cochereau](https://github.com/hugocoche)
