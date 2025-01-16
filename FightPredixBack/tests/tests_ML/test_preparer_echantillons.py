"""Descritpion:

Module de test de de la librairie prepare_sample
"""

from select_best_model.preparer_echantillons import (
    _creer_x_y,
    _symetrisation_resultat_du_combat,
    _symetrisation_explicative,
)
import pytest
import pandas as pd


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


def test_creer_x_y(data_fixture):
    """
    Test de la fonction _creer_x_y
    """

    X, y = _creer_x_y(data_fixture, "resultat", "poids_ml")
    assert X.shape == (4, 6)
    assert y.shape == (4, 2)


def test_symetrisation_explicative(data_fixture):
    """
    Test de la fonction _symetrisation_explicative
    """

    X, y = _creer_x_y(data_fixture, "resultat", "poids_ml")
    X_new = _symetrisation_explicative(X, ["combattant_1age"], ["cat"])

    assert X_new.shape == (8, 6)
    assert X_new["combattant_1age"].tolist() == [30, 25, 35, 40, -30, -25, -35, -40]
    assert X_new["combattant_1_cat"].tolist() == [
        "A",
        "B",
        "C",
        "D",
        "A",
        "B",
        "C",
        "D",
    ]


def test_symetrisation_resultat_du_combat(data_fixture):
    """
    Test de la fonction _symetrisation_resultat_du_combat
    """

    X, y = _creer_x_y(data_fixture, "resultat", "poids_ml")
    y_new = _symetrisation_resultat_du_combat(y)

    assert y_new.shape == (8, 2)
    assert y_new["resultat"].tolist() == [1, 0, 1, 0, 0, 1, 0, 1]
