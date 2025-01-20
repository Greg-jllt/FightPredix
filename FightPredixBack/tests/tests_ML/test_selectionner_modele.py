"""Description

Module de test pour la librairie selectionner_modele
"""

from sklearn.pipeline import Pipeline
from FightPredixBack.FightPredixML.selectionner_modele import (
    _comparer_score_entrainement,
    _tester_surapprentissage,
)
from sklearn.linear_model import LogisticRegression
import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def data_fixture():
    data = pd.DataFrame(
        {
            "combattant_1age": [30, 25, 35, 40],
            "combattant_2age": [25, 30, 40, 35],
            "combattant_1poids": [90, 100, 80, 70],
            "combattant_2poids": [100, 90, 70, 80],
            "combattant_1_cat": ["A", "B", "C", "D"],
            "combattant_2_cat": ["B", "C", "A", "D"],
            "resultat": [1, 0, 1, 0],
            "poids_ml": [0.5, 0.5, 0.5, 0.5],
        }
    )
    return data


def test_comparer_score_entrainement(data_fixture):
    """
    Test de la fonction _comparer_score_entrainement
    """

    modeles = [
        {
            "modele": "modele1",
            "score_entrainement": 0.8,
            "nom": "modele1",
        },
        {
            "modele": "modele2",
            "score_entrainement": 0.9,
            "nom": "modele2",
        },
    ]

    meilleur_modele = _comparer_score_entrainement(modeles)  # type: ignore

    assert meilleur_modele == "modele2"


def test_tester_surapprentissage(data_fixture):
    """
    Test de la fonction _tester_surapprentissage
    """
    modele = {
        "modele": Pipeline(
            [
                (
                    "classifier",
                    LogisticRegression().fit(
                        data_fixture.drop(
                            columns=[
                                "resultat",
                                "poids_ml",
                                "combattant_1_cat",
                                "combattant_2_cat",
                            ]
                        ).loc[:3],
                        data_fixture["resultat"].loc[:3],
                    ),
                )
            ]
        ),
        "score_entrainement": 0.8,
        "nom": "modele1",
    }

    modele2 = {
        "modele": Pipeline(
            [
                (
                    "classifier",
                    LogisticRegression().fit(
                        data_fixture.drop(
                            columns=[
                                "resultat",
                                "poids_ml",
                                "combattant_1_cat",
                                "combattant_2_cat",
                            ]
                        ).loc[:3],
                        data_fixture["resultat"].loc[:3],
                    ),
                )
            ]
        ),
        "score_entrainement": 0.0,
        "nom": "modele2",
    }

    X_test = data_fixture.drop(
        columns=["resultat", "poids_ml", "combattant_1_cat", "combattant_2_cat"]
    ).loc[[3]]
    y_test = data_fixture["resultat"].loc[3]

    score_test = modele["modele"].score(X_test, np.array([y_test]))
    score_test2 = modele2["modele"].score(X_test, np.array([y_test]))

    if score_test < 0.7:
        assert _tester_surapprentissage(X_test, np.array([y_test]), modele, seuil_surapprentissage=0.05)  # type: ignore
    else:
        assert not _tester_surapprentissage(X_test, np.array([y_test]), modele, seuil_surapprentissage=0.05)  # type: ignore

    if score_test2 < -0.1:
        assert _tester_surapprentissage(X_test, np.array([y_test]), modele2, seuil_surapprentissage=0.05)  # type: ignore
    else:
        assert not _tester_surapprentissage(X_test, np.array([y_test]), modele2, seuil_surapprentissage=0.05)  # type: ignore
