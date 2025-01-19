"""Description:

Vous retrouverez ici le processus d'optimisation des hyperparamètres pour les modèles et la sélection des meilleurs modèles pour chaque modèle de machine learning.
"""

from FightPredixBack.FightPredixML.preparer_echantillons import (
    _preparer_echantillons,
)
from FightPredixBack.FightPredixML.lib_optimisation import (
    _liste_features,
    _optimiser_modeles,
)
from FightPredixBack.FightPredixML.selectionner_modele import (
    _selectionner_meilleurs_modeles,
)
from rich.console import Console
import pandas as pd
import joblib
from FightPredixBack.outils import configure_logger
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_ML")


seuil_surapprentissage = 0.05
n_jobs = -2
random_state = 42
cv = 5
verbose = 1
test_size = 0.3


if __name__ == "__main__":
    console = Console()

    try:
        data = pd.read_json("FightPredixAPP/DataApp/Data_final_combats.json")
    except FileNotFoundError as e:
        console.print(f"[bold red]Erreur : {e}[/bold red]")
        exit()
    (
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    ) = _liste_features()
    logger.info("Préparation des échantillons...")
    X_train, X_test, y_train, y_test = _preparer_echantillons(
        data,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
        test_size,
        random_state,
    )

    logger.info("Optimisation des modèles...")
    logger.info(f"Variables numériques : {variables_numeriques}")
    logger.info(f"Variables catégorielles : {variables_categorielles}")
    logger.info(f"Variable à prédire : {variable_a_predire}")
    logger.info(
        f"""
        Vous avez choisi {n_jobs} coeurs pour l'optimisation des modèles.
        Vous avez choisi {cv} folds pour la validation croisée.
        Vous avez choisi {random_state} comme random_state.
        Vous avez choisi {verbose} comme verbose.
        """
    )
    dico_boosting, dico_logit, dico_random_forest, dico_neural_network, dico_svm = (
        _optimiser_modeles(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            n_jobs,
            random_state,
            verbose,
        )
    )

    logger.info(
        f"""
        Sélection du meilleur modèle...
        Le seuil de surapprentissage est de {seuil_surapprentissage}.
        """
    )
    best_model = _selectionner_meilleurs_modeles(
        X_test,
        y_test[variable_a_predire],
        modeles=[
            dico_boosting,
            dico_logit,
            dico_random_forest,
            dico_neural_network,
            dico_svm,
        ],
        seuil_surapprentissage=seuil_surapprentissage,
    )

    joblib.dump(best_model, "FightPredixApp/ModelApp/best_model.pkl")
