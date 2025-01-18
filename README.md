<p align="center">
  <img src="FightPredixApp/img/logo_readme.png" alt="Logo de mon projet" width="200" height="200">
</p>

## FightPredix

FightPredix est un package Python, faisant appel au scraping et au Machine Learning, permettant de prédire le résultat d'une éventuelle rencontre entre deux combattants de l'UFC. Le point centrale de ce package est la visualisation via `streamlit`.

La Structure du package est la suivante :
- [`FightPredixApp`](FightPredixApp/) : Le module contenant l'application Streamlit.
- [`FightPredixBack`](FightPredixBack/) :
  - [`FightPredixScraping`](FightPredixBack/FightPredixScraping/) : Le module contenant les fonctions de scraping.:
  - [`FightPredixConstructeur`](FightPredixBack/FightPredixConstructeur/) : Le module contenant les fonctions de construction des variables non initialement présentes.
  - [`FightPredixML`](FightPredixBack/FightPredixML/) : Le module contenant les fonctions de Machine Learning.

## Features

- Module entièrement documenté pour les interfaces publiques et privées.
- Formatage du code avec `Black` pour respecter les normes de PEP 8.
- Gestion des dépendances avec `uv`.
- Vérification des types avec `Mypy`.
- Développement d'une interface graphique avec `Streamlit`.

## Contributors

- [Gregory Jaillet](https://github.com/Greg-jllt)
- [Hugo Cochereau](https://github.com/hugocoche)
