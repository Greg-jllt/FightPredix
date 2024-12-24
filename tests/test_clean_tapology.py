"""
Module de test pour le nettoyage des données de Tapology
"""

import os
import sys
import polars as pl
import numpy as np

from FightPredix.lib_clean_tapology import (
    _get_closest_name,
    _manage_names,
    get_closest_streak,
    _create_streaks_variables,
    _reformat_date,
    _create_last_fight_variables,
    _create_home_variables,
    _birth_country,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_get_closest_name():
    """
    Test de la fonction _get_closest_name
    """
    assert (
        _get_closest_name(
            "Khabib Nurmagov",
            "Khabibibi Nurmagomedov",
            ["Khabib Nurmagomedov", "Khaha", "Jon Jones"],
        )
        == "Khabib Nurmagomedov"
    )
    assert (
        _get_closest_name(
            "Jon Jocelyn Jones", "Jon Jones", ["Jon Jones", "Khabib Nurmagomedov"]
        )
        == "Jon Jones"
    )


def test_manage_names():
    """
    Test de la fonction _manage_names
    """
    data_tapology = pl.DataFrame(
        {
            "NAME": ["Khabib Nurmagomedov", "Jon Jones", "Khabib Nurmagomedov"],
            "Given Name:tapology": [
                "Khabibibi Nurmagomedov",
                "Jon Jocelyn Jones",
                "Khabibibi Nurmagomedov",
            ],
        }
    )

    data_ufc = pl.DataFrame(
        {
            "NAME": ["Khabib Nurmagomedov", "Jon Jones", "Khabib Nurmagomedov"],
        }
    )

    assert np.all(
        _manage_names(data_tapology, data_ufc)["NAME"].to_numpy()
        == np.array(["Khabib Nurmagomedov", "Jon Jones", "Khabib Nurmagomedov"])
    )


def test_get_closest_streak():
    """
    Test de la fonction get_closest_streak
    """
    assert get_closest_streak("5 Win", ["5 Win", "3 Loss", "2 Win"]) == "5 Win"
    assert get_closest_streak("N/A", ["5 Win", "3 Loss", "2 Win"]) is None


def test_create_streaks_variables():
    """
    Test de la fonction _create_streaks_variables
    """
    data_tapology = pl.DataFrame(
        {
            "Current MMA Streak:tapology": ["5 Win", "3 Loss", "2 Win", None],
        }
    )

    assert np.all(
        _create_streaks_variables(data_tapology)[
            "Current Win Streak:tapology"
        ].to_list()
        == [5, 0, 2, None]
    )
    assert np.all(
        _create_streaks_variables(data_tapology)[
            "Current Lose Streak:tapology"
        ].to_list()
        == [0, 3, 0, None]
    )


def test_reformat_date():
    """
    Test de la fonction _reformat_date
    """
    assert _reformat_date("October 24, 2020") == "24/10/2020"
    assert _reformat_date("October 24, 2020", output_format="%Y-%m-%d") == "2020-10-24"


def test_create_last_fight_variables():
    """
    Test de la fonction _create_last_fight_variables
    """
    data_tapology = pl.DataFrame(
        {
            "Last Fight:tapology": [
                "October 24, 2020 \nin\n UFC",
                "January 24, 2020 \nin\n MMA",
                None,
            ],
        }
    )

    assert np.all(
        _create_last_fight_variables(data_tapology)[
            "Date of last fight:tapology"
        ].to_list()
        == ["24/10/2020", "24/01/2020", None]
    )

    assert np.all(
        _create_last_fight_variables(data_tapology)[
            "Organization of last fight:tapology"
        ].to_list()
        == ["UFC", "MMA", None]
    )


def test_create_home_variables():
    """
    Test de la fonction _create_home_variables
    """
    data_tapology = pl.DataFrame(
        {
            "Fighting out of:tapology": [
                "Paris, France",
                "New York, United States",
                "Paris",
                "England",
                "New York, New York, USA",
                "New York, USA",
                "USA",
                None,
                "New York, USA",
                "USA",
                None,
            ],
        }
    )

    assert np.all(
        _create_home_variables(data_tapology)["Country of residence:tapology"].to_list()
        == [
            "France",
            "United States",
            "France",
            "United Kingdom",
            "United States",
            "United States",
            "United States",
            None,
            "United States",
            "United States",
            None,
        ]
    )

    assert np.all(
        _create_home_variables(data_tapology)["City of residence:tapology"].to_list()
        == [
            "Paris",
            "New York",
            "Paris",
            None,
            "New York",
            "New York",
            None,
            None,
            "New York",
            None,
            None,
        ]
    )

    assert np.all(
        _create_home_variables(data_tapology)["State of residence:tapology"].to_list()
        == [
            "Ile-de-France",
            "New York",
            "Ile-de-France",
            "England",
            "New York",
            "New York",
            None,
            None,
            "New York",
            None,
            None,
        ]
    )


def test_birth_country():
    """
    Test de la fonction _birth_country
    """
    data_tapology = pl.DataFrame(
        {
            "Born:tapology": [
                "Paris, France",
                "New York, United States",
                "Paris",
                "England",
                "New York, New York, USA",
                "New York, USA",
                "USA",
                None,
                "New York, USA",
                "USA",
                None,
            ],
        }
    )

    assert np.all(
        _birth_country(data_tapology)["Country of birth:tapology"].to_list()
        == [
            "France",
            "United States",
            "France",
            "United Kingdom",
            "United States",
            "United States",
            "United States",
            None,
            "United States",
            "United States",
            None,
        ]
    )
