# FightPredixApp

<p align="center">
  <img src="img/logo_readme.png" alt="Logo de mon projet" width="200" height="200">
</p>

## Description

Ce module contient l'application web permettant de lancer des prédictions de combats.

## Requirement

- python3.13

## Installation

```bash
python -m pip install git+https://github.com/Greg-jllt/FightPredix.git
```

## Utilisation

> Si vous avez déjà installé le package, vous n'avez pas besoin d'initialiser un environnement virtuel pour l'utiliser.
Dans le cas contraire, suivez ces étapes :

1. **Cloner le package** avec la commande :

```bash
git clone https://github.com/Greg-jllt/FightPredix.git
```

2. Ouvrir un terminal dans le répertoire `FightPredixApp` du package avec la commande :

```bash
cd ./FightPredix/FightPredixApp
```

3. Créer un environnement virtuel:

> Il vous faudra tout d'abord installer le package `uv` avec la commande `python -m pip install uv`.

```bash
python -m uv venv
```

4. Installer les dépendances avec la commande :

```bash
python -m uv sync
```

5. Activer l'environnement virtuel avec la commande :

```bash
.venv\Scripts\activate
```

6. Lorsque vous voyez `(FightPredixApp)` dans votre terminal, cela indique que vous êtes dans l'environnement virtuel.
Cela signifie que toutes les commandes Python que vous exécutez fonctionneront dans cet environnement et auront accès aux dépendances installées.

7. Repositionnez-vous à la racine et lancez l'application avec la commande :

```bash
streamlit run FightPredixApp/app.py
```

![](img/présentation_app.gif)
