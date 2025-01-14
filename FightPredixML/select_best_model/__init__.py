from typing import Union
import joblib
from rich.console import Console
from sklearn.pipeline import Pipeline
import pandas as pd
from FightPredixML.select_best_model.optimiser_svm import _pipeline_svm
from FightPredixML.select_best_model.opitmiser_regression_logistique import (
    _pipeline_regression_logistique,
)
from FightPredixML.select_best_model.opitmiser_random_forest import (
    _pipeline_random_forest,
)
from FightPredixML.select_best_model.optimiser_neural_network import (
    _pipeline_neural_network,
)
from FightPredixML.select_best_model.opitmiser_boosting import _pipeline_boosting
from FightPredixML.select_best_model.grille_de_parametres import (
    parametres_boosting,
    parametres_random_forest,
    parametres_regression_logistique,
    parametres_neural_network,
    parametres_svm,
)


def _liste_features() -> tuple[list[str], list[str], str, str]:
    """
    Renvoie des listes de variables utilisables pour le machine learning
    """

    variables_numeriques = [
        "diff_age_t",
        "diff_win_t",
        "diff_losses_t",
        "diff_forme",
        "diff_serie",
        "diff_sig_str_total_reussi_moyenne",
        "diff_sig_str_total_total_moyenne",
        "diff_total_str_total_reussi_moyenne",
        "diff_total_str_total_total_moyenne",
        "diff_tdtotal_reussi_moyenne",
        "diff_tdtotal_total_moyenne",
        "diff_headsig_str_total_reussi_moyenne",
        "diff_headsig_str_total_total_moyenne",
        "diff_bodysig_str_total_reussi_moyenne",
        "diff_bodysig_str_total_total_moyenne",
        "diff_legsig_str_total_reussi_moyenne",
        "diff_legsig_str_total_total_moyenne",
        "diff_distancesig_str_total_reussi_moyenne",
        "diff_distancesig_str_total_total_moyenne",
        "diff_clinchsig_str_total_reussi_moyenne",
        "diff_clinchsig_str_total_total_moyenne",
        "diff_groundsig_str_total_reussi_moyenne",
        "diff_groundsig_str_total_total_moyenne",
        "diff_frappe_tete_moyenne",
        "diff_frappe_corps_moyenne",
        "diff_frappe_jambe_moyenne",
        "diff_frappe_distance_moyenne",
        "diff_frappe_clinch_moyenne",
        "diff_frappe_sol_moyenne",
        "diff_kdtotal_moyenne",
        "diff_sig_str_total_ratio_moyenne",
        "diff_sig_str_percent_total_moyenne",
        "diff_total_str_total_ratio_moyenne",
        "diff_tdtotal_ratio_moyenne",
        "diff_td_percent_total_moyenne",
        "diff_sub_atttotal_moyenne",
        "diff_revtotal_moyenne",
        "diff_ctrltotal_moyenne",
        "diff_headsig_str_total_ratio_moyenne",
        "diff_bodysig_str_total_ratio_moyenne",
        "diff_legsig_str_total_ratio_moyenne",
        "diff_distancesig_str_total_ratio_moyenne",
        "diff_clinchsig_str_total_ratio_moyenne",
        "diff_groundsig_str_total_ratio_moyenne",
        "diff_la_taille",
        "diff_poids",
        "diff_reach",
        "diff_portee_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_dec",
        "diff_ko/tko",
        "diff_sub",
    ]

    variables_categorielles = [
        "combattant_1_style_de_combat",
        "combattant_2_style_de_combat",
        "combattant_1_country_of_residence_tapology",
        "combattant_2_country_of_residence_tapology",
        "combattant_1_country_of_birth_tapology",
        "combattant_2_country_of_birth_tapology",
    ]

    variable_a_predire = "resultat"

    variable_de_poids = "poids_ml"

    return (
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )


ModelDict = dict[str, Union[str, Pipeline, float]]


def _optimiser_modeles(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
) -> tuple[ModelDict, ModelDict, ModelDict, ModelDict, ModelDict]:
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
        parametres_boosting,
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
        parametres_regression_logistique,
    )

    Console().print("Optimisation du modèle random forest...", style="bold green")
    dico_random_forest = _pipeline_random_forest(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
        parametres_random_forest,
    )

    Console().print("Optimisation du modèle neural network...", style="bold green")
    dico_neural_network = _pipeline_neural_network(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
        parametres_neural_network,
    )

    Console().print("Optimisation du modèle SVM...", style="bold green")
    dico_svm = _pipeline_svm(
        X_train,
        y_train,
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
        parametres_svm,
    )

    return (
        dico_boosting,
        dico_logit,
        dico_random_forest,
        dico_neural_network,
        dico_svm,
    )


def _sauvegarder_modeles(
    boosting: Pipeline,
    logit: Pipeline,
    random_forest: Pipeline,
    neural_network: Pipeline,
    svm: Pipeline,
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


class ModelOptmizationError(Exception):
    """Exception levée lorsque l'optimisation du modèle échoue"""

    def __init__(self, message: str):
        super().__init__(message)
