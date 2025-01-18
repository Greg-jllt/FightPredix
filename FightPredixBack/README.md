# FightPredixBack

<p align="center">
  <img src="../FightPredixApp/img/logo_readme.png" alt="Logo de mon projet" width="200" height="200">
</p>

## Description

Bienvenue dans `FightPredixBack`. Ce module regroupe l'ensemble des outils et des bibliothèques utilisés pour construire les données nécessaires à `FightPredix`. Il se divise en trois parties distinctes :

1. **FightPredixScraping**
   Cette section du module contient les scripts utilisés pour récupérer des données provenant de **quatre** sites différents :
   - [UFC.com](https://www.ufc.com/) : Le site officiel de l'UFC, fournissant des informations complètes sur les événements, les combattants et les statistiques.
   - [UFC stats](http://www.ufcstats.com/statistics/events/completed) : Une base de données exhaustive des statistiques des combats de l'UFC.
   - [UFC fans](https://www.ufc-fr.com/) : Un site communautaire pour les fans de l'UFC, offrant des analyses et des discussions sur les combats.
   - [Tapology](https://www.tapology.com/) : Un site de référence pour les classements et les statistiques des combattants de MMA.

   Pour plus d'informations sur cette partie du module, veuillez consulter le [README de FightPredixScraping](./FightPredixScraping/).

2. **FightPredixConstructeur**
   Cette section du module est dédiée à la construction des variables à partir des données récupérées. Elle permet de transformer les données brutes en un format exploitable pour les analyses et les modèles prédictifs.

   Pour plus d'informations sur cette partie du module, veuillez consulter le [README de FightPredixConstructeur](./FightPredixConstructeur/).

3. **FightPredixML**
   Cette section du module utilise la base de données finale pour construire les modèles prédictifs les plus performants possibles parmi les algorithmes suivants :
   - `GradientBoostingClassifier` : Un modèle de boosting qui combine plusieurs arbres de décision pour améliorer la précision des prédictions.
   - `LogisticClassifier` : Un modèle de régression logistique utilisé pour les tâches de classification binaire.
   - `RandomForestClassifier` : Un ensemble d'arbres de décision qui améliore la précision et réduit le surapprentissage.
   - `MLPClassifier` : Un perceptron multicouche, un type de réseau de neurones artificiels utilisé pour les tâches de classification.
   - `SVC` : Un classificateur à vecteurs de support, efficace pour les tâches de classification avec des marges maximales.

   Pour plus d'informations sur cette partie du module, veuillez consulter le [README de FightPredixML](./FightPredixML/).

Nous espérons que ce module vous sera utile pour vos analyses et prédictions dans le domaine des combats de l'UFC. N'hésitez pas à consulter les documentations spécifiques de chaque partie pour des informations détaillées et des exemples d'utilisation.

## Prérequis

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

2. Ouvrir un terminal dans le répertoire `FightPredixBack` du package avec la commande :

```bash
cd ./FightPredix/FightPredixBack
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

6. Lorsque vous voyez `(FightPredixBack)` dans votre terminal, cela indique que vous êtes dans l'environnement virtuel.
Cela signifie que toutes les commandes Python que vous exécutez fonctionneront dans cet environnement et auront accès aux dépendances installées.

7. Repositionnez-vous à la racine du projet

```bash
cd ..
```

**ATTENTION** :

- **L'étape suivante ne vous est actuellement pas nécessaire puisque la base de données est déjà construite**
- **Lancer et terminer ce processus conduira à l'écrasement de la base de données actuelle. Vous aurez tout de même la possibilité de récupérer l'ancienne base en reclonant le projet**
- **Ce processus peut-être assez couteux en temps et en calcul.**

8. Lancez le module souhaité (FightPredixScraping, FightPredixConstructeur ou FightPredixML), si vous souhaitez reconstruire totalement les données alors lancez les différents modules dans l'ordre suivant :

```bash
python -m FightPredixBack.FightPredixScraping
python -m FightPredixBack.FightPredixConstructeur
python -m FightPredixBack.FightPredixML
```

## Fonctionnalités

- Module entièrement documenté pour les interfaces publiques et privées.
- Formatage du code avec `Black` pour respecter les normes de PEP 8.
- Gestion des dépendances avec `uv`.
- Vérification des types avec `Mypy`.
- Tests unitaires avec `pytest` et couverture de test avec `pytest-cov` :
   - Positionnez-vous dans le répertoire racine : `FightPredix`
   - Tester l'application avec la commande `python -m pytest`

## Contributeurs

- [Gregory Jaillet](https://github.com/Greg-jllt)
- [Hugo Cochereau](https://github.com/hugocoche)
