"""
Module de test pour la librairie lib_constructeur.py
"""

import pandas as pd
import numpy as np

from datetime import datetime


from FightPredixBack.FightPredixConstructeur.lib_constructeur import (
    _difference_num_combats,
    _age_by_DOB,
    _transformation_debut_octogone,
    _nettoyage_nom_colonne,
    _process_valeur,
    _process_ratio,
    _cleaning,
    _sub_fonction_age,
    _age_temps_t,
    _calcul_victoires_defaites,
    _calcul_forme_combattant,
    _calcul_statistique_generique,
)


def test_difference_combats():
    """
    Test de la fonction _difference_combats
    """

    combats = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "combattant_1_age": [30, 25],
            "combattant_2_age": [25, 30],
            "combattant_1_height": [180, 170],
            "combattant_2_height": [170, 180],
            "combattant_1_weight": [80, 75],
            "combattant_2_weight": [75, 80],
        }
    )

    combats = _difference_num_combats(combats)

    assert combats["diff_age"].tolist() == [5, -5]
    assert combats["diff_height"].tolist() == [10, -10]
    assert combats["diff_weight"].tolist() == [5, -5]


def test_age_by_DOB():
    """
    Test de la fonction _age_by_DOB
    """
    data = pd.DataFrame(
        {
            "NAME": ["JOHN DOE", "JANE DOE"],
            "ÂGE": [35, np.nan],
            "DOB": ["Jan 1, 1990", "Jan 1, 1995"],
        }
    )

    data = _age_by_DOB(data)

    assert data["ÂGE"].tolist() == [35, 30]


def test_transformation_debut_octogone():
    """
    Test de la fonction _transformation_debut_octogone
    """
    data = pd.DataFrame(
        {
            "DÉBUT DE L'OCTOGONE": ["Jan. 1, 2020", "Jan. 1, 2021"],
        }
    )

    data = _transformation_debut_octogone(data)

    assert data["DÉBUT DE L'OCTOGONE"].tolist() == [61, 49]


def test_clean_column_nom():
    """
    Test de la fonction clean_column_nom
    """
    assert _nettoyage_nom_colonne("John Doe") == "john_doe"
    assert _nettoyage_nom_colonne("John Doe 2") == "john_doe_2"
    assert _nettoyage_nom_colonne("John Doe 2!") == "john_doe_2_"


def test_process_valeur():
    """
    Test de la fonction _process_valeur
    """
    assert _process_valeur("10%") == 0.1
    assert _process_valeur("10:30") == 630
    assert _process_valeur("---") is None


def test_process_ratio():
    """
    Test de la fonction _process_ratio
    """
    assert _process_ratio("10 of 20") == (10, 20, 0.5)
    assert _process_ratio("10 of 0") == (10, 0, np.nan)


def test_cleaning():
    """
    Test de la fonction _cleaning
    """
    data = pd.DataFrame(
        {
            "col1": ["10 of 20"],
            "col2": ["10:30"],
            "col3": ["30%"],
        }
    )

    data = _cleaning(data)

    assert data["col1_reussi"].tolist() == [10.0]
    assert data["col1_total"].tolist() == [20.0]
    assert data["col1_ratio"].tolist() == [0.5]
    assert data["col2"].tolist() == [630]
    assert data["col3"].tolist() == [0.3]


def test_sub_fonction_age():
    """
    Test de la fonction _sub_fonction_age
    """
    data = pd.DataFrame(
        {
            "name": ["John Doe", "Jane Doe"],
            "âge": [35, 30],
            "dob": ["Jan 1, 1990", "Jan 1, 1995"],
        }
    )

    assert _sub_fonction_age(data, "John Doe", 2021, datetime.now()) == 31
    assert _sub_fonction_age(data, "Jane Doe", 2021, datetime.now()) == 26


def test_age_temps_t():
    """
    Test de la fonction _age_temps_t
    """
    data = pd.DataFrame(
        {
            "name": ["John Doe", "Jane Doe"],
            "âge": [35, 30],
            "dob": ["Jan 1, 1990", "Jan 1, 1995"],
        }
    )

    combats = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "date": [datetime.now(), datetime.now()],
        }
    )

    combats = _age_temps_t(data, combats)

    assert combats["combattant_1_age_t"].tolist() == [35, 30]
    assert combats["combattant_2_age_t"].tolist() == [30, 35]


def test_victoires_defaites_temps_t():
    """
    Test de la fonction _win_losses_temps_t et plus généralement de la fonction _calcul_statistiques_generique
    """

    combats = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "combattant_1_nickname": ["John", "Jane"],
            "combattant_2_nickname": ["Jane", "John"],
            "resultat": [0, 1],
        }
    )

    combats = _calcul_statistique_generique(combats, _calcul_victoires_defaites)

    assert combats["combattant_1_win_t"].tolist() == [1, 0]
    assert combats["combattant_1_losses_t"].tolist() == [0, 0]
    assert combats["combattant_2_win_t"].tolist() == [0, 0]
    assert combats["combattant_2_losses_t"].tolist() == [1, 0]


def test_forme_combattant():
    """
    Test de la fonction de forme des combattants et plus généralement de la fonction _calcul_statistiques_generique
    """

    combats = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "combattant_1_nickname": ["John", "Jane"],
            "combattant_2_nickname": ["Jane", "John"],
            "resultat": [0, 1],
        }
    )

    combats = _calcul_statistique_generique(combats, _calcul_forme_combattant)

    assert combats["combattant_1_forme"].tolist() == [1, 0]
    assert combats["combattant_2_forme"].tolist() == [-1, 0]
