# Package de scraping de l'application FightPredix

<p align="center">
  <img src="../FightPredixApp/img/logo.png" alt="Logo de mon projet" width="200" height="200">
</p>

# Requirement

- python3.10

# Installation

```bash
python -m pip install git+https://github.com/Greg-jllt/Projet_UFC.git
```

# Utilisation

> Si vous avez déjà installé le package, vous n'avez pas besoin d'initialiser un environnement virtuel pour l'utiliser.  
Dans le cas contraire, suivez ces étapes :  

1. **Cloner le package** avec la commande :  

```bash
git clone https://github.com/hugocoche/BatchMonitor.git
```

2. Ouvrir un terminal dans le répertoire racine du package avec la commande :

```bash
cd ./BatchMonitor
```

3. Créer un environnement virtuel et installer les dépendances avec la commande :

```bash
python -m poetry install
```

4. Activer l'environnement virtuel avec la commande :

```bash
python -m poetry shell
```

5. Lorsque vous voyez `(batchmonitor-py3.11)` dans votre terminal, cela indique que vous êtes dans l'environnement virtuel.
Cela signifie que toutes les commandes Python que vous exécutez fonctionneront dans cet environnement et auront accès aux dépendances installées.

# Features

- Module entièrement documenté pour les interfaces publiques et privées.
- Formatage du code avec `Black` pour respecter les normes de PEP 8.
- Gestion des dépendances avec `uv`.
- Vérification des types avec `Mypy`.
- Développement d'une interface graphique avec `Streamlit`.
- Tests unitaires et d'intégration avec `Pytest`, et couverture de tests avec `Pytest-cov`.

# Contributors

- [Gregory Jaillet](https://github.com/Greg-jllt)
- [Hugo Cochereau](https://github.com/hugocoche)
