"""
Module de test pour la librairie lib_constructeur.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
from scraping.lib_constructeur import (
    _difference_combats,
    _age_by_DOB,
    _transformation_debut_octogone,
    clean_column_nom,
    _process_valeur,
    _process_ratio,
    _cleaning,
    _sub_fonction_age,
    _age_temps_t,
    _win_losses_temps_t,
)


def test_difference_combats():
    """
    Test de la fonction _difference_combats
    """

    caracteristiques = pd.DataFrame(
        {
            "name": ["John Doe", "Jane Doe"],
            "age": [30, 25],
            "height": [180, 170],
            "weight": [80, 75],
        }
    )

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

    combats = _difference_combats(caracteristiques, combats)

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

    assert data["DÉBUT DE L'OCTOGONE"].tolist() == [61, 48]


def test_clean_column_nom():
    """
    Test de la fonction clean_column_nom
    """
    assert clean_column_nom("John Doe") == "john_doe"
    assert clean_column_nom("John Doe 2") == "john_doe_2"
    assert clean_column_nom("John Doe 2!") == "john_doe_2_"


def test_process_valeur():
    """
    Test de la fonction _process_valeur
    """
    assert _process_valeur("10 of 20") == 20
    assert _process_valeur("10%") == 0.1
    assert _process_valeur("10:30") == 630
    assert _process_valeur("---") is None


def test_process_ratio():
    """
    Test de la fonction _process_ratio
    """
    assert _process_ratio("10 of 20") == 0.5
    assert np.isnan(_process_ratio("10 of 0"))


def test_cleaning():
    """
    Test de la fonction _cleaning
    """
    data = pd.DataFrame(
        {
            "col1": ["10 of 20", "10%"],
            "col2": ["10:30", "30%"],
        }
    )

    data = _cleaning(data)

    assert data["col1"].tolist() == [20, 0.1]
    assert data["col2"].tolist() == [630, 0.3]


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
            "date": ["January 2, 2021", "January 2, 2021"],
        }
    )

    combats = _age_temps_t(data, combats)

    assert combats["combattant_1_age_t"].tolist() == [31, 26]
    assert combats["combattant_2_age_t"].tolist() == [26, 31]


def test_win_losses_temps_t():
    """
    Test de la fonction _win_losses_temps_t
    """
    data = pd.DataFrame(
        {
            "name": ["John Doe", "Jane Doe"],
            "win": [10, 20],
            "losses": [5, 10],
        }
    )

    combats = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "resultat": [0, 1],
        }
    )

    combats = _win_losses_temps_t(data, combats)

    breakpoint()

    assert combats["combattant_1_win_t"].tolist() == [9, 20]
    assert combats["combattant_1_losses_t"].tolist() == [5, 9]
    assert combats["combattant_2_win_t"].tolist() == [20, 8]
    assert combats["combattant_2_losses_t"].tolist() == [8, 5]
