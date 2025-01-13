"""Description:

Vous retrouverez ici le processus d'optimisation des hyperparamètres pour les modèles et la sélection des meilleurs modèles pour chaque modèle de machine learning.
"""

from FightPredixML.select_best_model.preparer_echantillons import _preparer_echantillons
from FightPredixML.select_best_model import _liste_features
from FightPredixML.select_best_model.selectionner_modele import (
    _selectionner_meilleurs_modeles,
)
import joblib
from FightPredixML.select_best_model.optimiser_svm import _pipeline_svm
from FightPredixML.select_best_model.opitmiser_regression_logistique import (
    _pipeline_regression_logistique,
)
from FightPredixML.select_best_model.opitmiser_random_forest import (
    _pipeline_random_forest,
)

# from lib_ML.optimiser_naive_bayes import _pipeline_naive_bayes
from FightPredixML.select_best_model.optimiser_neural_network import (
    _pipeline_neural_network,
)
from FightPredixML.select_best_model.opitmiser_boosting import _pipeline_boosting
from rich.console import Console
import pandas as pd
from sklearn.pipeline import Pipeline


def _optimiser_modeles(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
) -> dict[dict[str, Pipeline, float]]:
    """
    Cette fonction permet d'optimiser les modèles
    """

    Console().print("Optimisation du modèle boosting...", style="bold green")
    dico_boosting = _pipeline_boosting(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    Console().print(
        "Optimisation du modèle regression logistique...", style="bold green"
    )
    dico_logit = _pipeline_regression_logistique(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    Console().print("Optimisation du modèle random forest...", style="bold green")
    dico_random_forest = _pipeline_random_forest(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    Console().print("Optimisation du modèle neural network...", style="bold green")
    dico_neural_network = _pipeline_neural_network(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    Console().print("Optimisation du modèle SVM...", style="bold green")
    dico_svm = _pipeline_svm(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )

    # Console().print("Optimisation du modèle Naive Bayes...", style="bold green")
    # dico_naive_bayes = _pipeline_naive_bayes(
    #     X_train,
    #     y_train,
    #     variables_numeriques,
    #     variables_categorielles,
    #     variable_a_predire,
    #     variable_de_poids,
    # )
    return (
        dico_boosting,
        dico_logit,
        dico_random_forest,
        dico_neural_network,
        dico_svm,
        # dico_naive_bayes
    )


def _sauvegarder_modeles(
    boosting: Pipeline,
    logit: Pipeline,
    random_forest: Pipeline,
    neural_network: Pipeline,
    svm: Pipeline,
    # naive_bayes: Pipeline,
) -> None:
    """
    Cette fonction permet de sauvegarder les modèles
    """
    Console().print("Sauvegarde des modèles...", style="bold green")
    joblib.dump(boosting, "FightPredixML/modele/boosting.pkl")
    joblib.dump(logit, "FightPredixML/modele/logistic_regression.pkl")
    joblib.dump(random_forest, "FightPredixML/modele/random_forest.pkl")
    joblib.dump(neural_network, "FightPredixML/modele/neural_network.pkl")
    joblib.dump(svm, "FightPredixML/modele/svm.pkl")


if __name__ == "__main__":
    console = Console()

    data = pd.read_json("FightPredixML/DataML/Data_final_combats.json")
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

    _sauvegarder_modeles(
        dico_boosting["modele"],
        dico_logit["modele"],
        dico_random_forest["modele"],
        dico_neural_network["modele"],
        dico_svm["modele"],
        # dico_naive_bayes["modele"],
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
            # dico_naive_bayes,
        ],
    )

    if best_model is not None:
        joblib.dump(best_model, "FightPredixApp/ModelApp/best_model.pkl")
