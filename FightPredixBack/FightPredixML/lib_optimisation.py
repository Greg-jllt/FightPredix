"""Description:

Ce fichier contient les outils utilisés pour l'optimisation des modèles"""

import joblib
from typing import Union
import pandas as pd
from sklearn.pipeline import Pipeline
from FightPredixBack.FightPredixML.opitmiser_boosting import _pipeline_boosting
from FightPredixBack.FightPredixML.opitmiser_random_forest import (
    _pipeline_random_forest,
)
from FightPredixBack.FightPredixML.opitmiser_regression_logistique import (
    _pipeline_regression_logistique,
)
from FightPredixBack.FightPredixML.optimiser_neural_network import (
    _pipeline_neural_network,
)
from FightPredixBack.FightPredixML.optimiser_svm import _pipeline_svm
from FightPredixBack.FightPredixML.grille_de_parametres import (
    parametres_boosting,
    parametres_random_forest,
    parametres_regression_logistique,
    parametres_neural_network,
    parametres_svm,
)
from FightPredixBack.outils import configure_logger
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_optimisation")


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
        "diff_total_str_total_ratio_moyenne",
        "diff_tdtotal_ratio_moyenne",
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
        "diff_ko_tko",
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
    cv: int,
    n_jobs: int,
    random_state: int,
    verbose: int,
) -> tuple[ModelDict|None, ModelDict|None, ModelDict|None, ModelDict|None, ModelDict|None]:
    """
    Cette fonction permet d'optimiser les modèles
    """
    
    dico_boosting = None
    dico_logit = None
    dico_random_forest = None
    dico_neural_network = None
    dico_svm = None

    logger.info(
        f"""
        Optimisation du modèle boosting...
        La grille de paramètres est la suivante : {parametres_boosting}
                """
    )
    try:
        dico_boosting = _pipeline_boosting(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            parametres_boosting,
            n_jobs,
            random_state,
            verbose,
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation du modèle boosting : {e}")

    joblib.dump(
        dico_boosting["modele"], "FightPredixBack/FightPredixML/modele/boosting.pkl"
    )

    logger.info(
        f"""
        Optimisation du modèle regression logistique...
        La grille de paramètres est la suivante : {parametres_regression_logistique}
        """
    )
    try:
        dico_logit = _pipeline_regression_logistique(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            parametres_regression_logistique,
            n_jobs,
            random_state,
            verbose,
        )
        logger.info(f"""Modèle regression logistique optimisé : {dico_logit}""")
        joblib.dump(
            dico_logit["modele"],
            "FightPredixBack/FightPredixML/modele/logistic_regression.pkl",
        )
    except Exception as e:
        logger.error(
            f"Erreur lors de l'optimisation du modèle regression logistique : {e}"
        )

    logger.info(f"""
                Optimisation du modèle random forest...
                La grille de paramètres est la suivante : {parametres_random_forest}
                """)
    try:
        dico_random_forest = _pipeline_random_forest(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            parametres_random_forest,
            n_jobs,
            random_state,
            verbose,
        )
        joblib.dump(
            dico_random_forest["modele"],
            "FightPredixBack/FightPredixML/modele/random_forest.pkl",
        )
        logger.info(f"""Modèle random forest optimisé : {dico_random_forest}""")
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation du modèle random forest : {e}")

    logger.info(f"""
                Optimisation du modèle neural network...
                La grille de paramètres est la suivante : {parametres_neural_network}
                """)
    try:
        dico_neural_network = _pipeline_neural_network(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            parametres_neural_network,
            n_jobs,
            random_state,
            verbose,
        )
        joblib.dump(
            dico_neural_network["modele"],
            "FightPredixBack/FightPredixML/modele/neural_network.pkl",
        )
        logger.info(f"""Modèle neural network optimisé : {dico_neural_network}""")
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation du modèle neural network : {e}")

    logger.info(f"""
                Optimisation du modèle SVM...
                La grille de paramètres est la suivante : {parametres_svm}
                """)
    try:
        dico_svm = _pipeline_svm(
            X_train,
            y_train,
            variables_numeriques,
            variables_categorielles,
            variable_a_predire,
            variable_de_poids,
            cv,
            parametres_svm,
            n_jobs,
            random_state,
            verbose,
        )
        joblib.dump(dico_svm["modele"], "FightPredixBack/FightPredixML/modele/svm.pkl")
        logger.info(f"""Modèle SVM optimisé : {dico_svm}""")
    except Exception as e:
        logger.error(f"Erreur lors de l'optimisation du modèle SVM : {e}")

    return (
        dico_boosting,
        dico_logit,
        dico_random_forest,
        dico_neural_network,
        dico_svm,
    )
