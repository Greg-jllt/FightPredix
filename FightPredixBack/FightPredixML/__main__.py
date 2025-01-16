"""Description:

Vous retrouverez ici le processus d'optimisation des hyperparamètres pour les modèles et la sélection des meilleurs modèles pour chaque modèle de machine learning.
"""

from FightPredixBack.FightPredixML.select_best_model.preparer_echantillons import (
    _preparer_echantillons,
)
from FightPredixBack.FightPredixML.select_best_model import (
    _liste_features,
    _optimiser_modeles,
    _sauvegarder_modeles,
)
from FightPredixBack.FightPredixML.select_best_model.selectionner_modele import (
    _selectionner_meilleurs_modeles,
)
from rich.console import Console
import pandas as pd
import joblib


seuil_surapprentissage = 0.05
sauvegarder_les_modeles = True

if __name__ == "__main__":
    console = Console()

    data = pd.read_json("FightPredixAPP/DataApp/Data_final_combats.json")
    (
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    ) = _liste_features()
    console.print("Préparation des échantillons...", style="bold green")
    X_train, X_test, y_train, y_test = _preparer_echantillons(
        data,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    console.print("Optimisation des modèles...", style="bold green")
    dico_boosting, dico_logit, dico_random_forest, dico_neural_network, dico_svm = (
        _optimiser_modeles(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
        )
    )

    if sauvegarder_les_modeles:
        _sauvegarder_modeles(
            dico_boosting["modele"],
            dico_logit["modele"],
            dico_random_forest["modele"],
            dico_neural_network["modele"],
            dico_svm["modele"],
        )

    console.print(
        "Sélection des meilleurs modèles parmi les modèles optimisés : boosting, logit, random_forest, naive_bayes, neural_network, svm",
        style="bold green",
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

    if best_model is not None:
        joblib.dump(best_model, "FightPredixApp/ModelApp/best_model.pkl")
