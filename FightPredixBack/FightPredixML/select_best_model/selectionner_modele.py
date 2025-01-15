"""Description:

Module permettant de sélectionner le modèle le plus performant pour chaque modèle de machine learning entrainé
"""

from typing import Any
from sklearn.pipeline import Pipeline
import pandas as pd
from rich.console import Console


def _comparer_score_entrainement(
    modeles: list[dict[str, Any]],
) -> Pipeline:
    """
    Cette fonction permet de comparer les scores des différents modèles
    """

    meilleur_score = 0.0
    for modele in modeles:
        if modele["score_entrainement"] > meilleur_score:
            meilleur_score = modele["score_entrainement"]
            meilleur_modele = modele["modele"]
            nom_meilleur_modele = modele["nom"]
    Console().print(
        f"Le meilleur modèle est {nom_meilleur_modele} avec un score de {meilleur_score}",
        style="bold green",
    )
    return meilleur_modele


def _tester_surapprentissage(
    X_test: pd.DataFrame,
    y_test: pd.DataFrame,
    modele: dict[str, Any],
    seuil_surapprentissage: float = 0.05,
) -> bool:
    """
    Cette fonction permet de vérifier le surapprentissage, le critère retenu est une différence de -0.05 entre le score d'entrainement et le score de validation
    """

    score_test = modele["modele"].score(X_test, y_test)

    diff_score_entrainement_test = modele["score_entrainement"] - score_test

    if diff_score_entrainement_test > seuil_surapprentissage:
        Console().print(
            f"Le modèle {modele['nom']} a été retiré car il surapprend : différence de {diff_score_entrainement_test} entre le score d'entrainement et le score de test",
            style="bold red",
        )
        return True
    Console().print(
        f"Le modèle {modele['nom']} n'a pas été retiré car il ne surapprend pas : différence de {diff_score_entrainement_test} entre le score d'entrainement et le score de test",
        style="bold green",
    )
    return False


def _selectionner_meilleurs_modeles(
    X_test: pd.DataFrame,
    y_test: pd.Series,
    modeles: list[dict[str, Any]],
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
        raise Warning("Aucun modèle n'a été sélectionné car tous surapprennent")
    else:
        return _comparer_score_entrainement(liste_modeles)
