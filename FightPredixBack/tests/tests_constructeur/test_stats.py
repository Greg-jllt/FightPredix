"""
Module de test pour la librairie lib_stats.py
"""

import pandas as pd


from FightPredixBack.FightPredixConstructeur.lib_stats import (
    _calcul_stat_cumul,
    _format_date,
    _sub_format_date,
)


def test_sub_format_date():
    """
    Test de la fonction _sub_format_date
    """

    date = "January 01, 2021"
    format_actuel = "%B %d, %Y"
    format_voulu = "%Y-%m-%d"

    assert _sub_format_date(date, format_actuel, format_voulu) == "2021-01-01"


def test_format_date():
    """
    Test de la fonction _format_date
    """

    data = pd.DataFrame(
        {
            "date": ["January 01, 2021", "February 02, 2022"],
        }
    )

    _format_date(data)

    assert data["date"].tolist() == ["2021-01-01", "2022-02-02"]


def test_calcul_stat_cumul():
    """
    Test de la fonction _calcul_stat_cumul
    """

    data = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "combattant_1_height": [180, 170],
            "combattant_2_height": [170, 180],
            "combattant_1_weight": [80, 75],
            "combattant_2_weight": [75, 80],
        }
    )

    data_combattant = pd.DataFrame(
        {
            "combattant_1": ["John Doe", "Jane Doe"],
            "combattant_2": ["Jane Doe", "John Doe"],
            "combattant_1_height": [180, 170],
            "combattant_2_height": [170, 180],
            "combattant_1_weight": [80, 75],
            "combattant_2_weight": [75, 80],
        }
    )

    nom = "John Doe"
    dico_var = {
        "combattant_height": ("combattant_1_height", "combattant_2_height"),
        "combattant_weight": ("combattant_1_weight", "combattant_2_weight"),
    }

    data, _ = _calcul_stat_cumul(data, data_combattant, nom, dico_var)

    assert pd.isna(data["combattant_2_height_moyenne"].tolist()[0])
    assert pd.isna(data["combattant_2_weight_moyenne"].tolist()[0])
