"""Description:

Module permettant de sélectionner le modèle le plus performant pour chaque modèle de machine learning entrainé
"""

from sklearn.pipeline import Pipeline
import pandas as pd
from datetime import datetime
from FightPredixBack.outils import configure_logger
from typing import Union

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_selection_modele")

ModelDict = dict[str, Union[str, Pipeline, float]]


def _comparer_score_entrainement(
    modeles: list[ModelDict | None],
) -> Pipeline:
    """
    Cette fonction permet de comparer les scores des différents modèles
    """

    meilleur_score = 0.0
    for modele in modeles:
        if modele and modele["score_entrainement"] > meilleur_score:
            meilleur_score = modele["score_entrainement"]
            meilleur_modele = modele["modele"]
            nom_meilleur_modele = modele["nom"]
    logger.info(
        f"Le meilleur modèle est {nom_meilleur_modele} avec un score de {meilleur_score}"
    )
    return meilleur_modele


def _tester_surapprentissage(
    X_test: pd.DataFrame,
    y_test: pd.DataFrame,
    modele: ModelDict,
    seuil_surapprentissage: float = 0.05,
) -> bool:
    """
    Cette fonction permet de vérifier le surapprentissage, le critère retenu est une différence de -0.05 entre le score d'entrainement et le score de validation
    """

    score_test = modele["modele"].score(X_test, y_test)

    diff_score_entrainement_test = modele["score_entrainement"] - score_test

    if diff_score_entrainement_test > seuil_surapprentissage:
        logger.info(
            f"Le modèle {modele['nom']} a été retiré car il surapprend : différence de {diff_score_entrainement_test} entre le score d'entrainement et le score de test"
        )
        return True
    logger.info(
        f"Le modèle {modele['nom']} n'a pas été retiré car il ne surapprend pas : différence de {diff_score_entrainement_test} entre le score d'entrainement et le score de test"
    )
    return False


def _selectionner_meilleurs_modeles(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    modeles: list[ModelDict],
    seuil_surapprentissage: float = 0.05,
) -> Pipeline | None:
    """
    Cette fonction permet de sélectionner le meilleur modèle
    """
    liste_modeles = [modele for modele in modeles]
    for modele in modeles:
        if _tester_surapprentissage(X_test, y_test, modele, seuil_surapprentissage):
            liste_modeles.remove(modele)
    if len(liste_modeles) == 0:
        logger.warning("Aucun modèle n'a été sélectionné car tous surapprennent")
    else:
        return _comparer_score_entrainement(liste_modeles)
