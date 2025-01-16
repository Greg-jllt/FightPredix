"""
Module de test pour le nettoyage des données de Tapology
"""

import polars as pl
import numpy as np

from FightPredixBack.FightPredixScraping.scraping.lib_nettoyage_tapology import (
    _create_streaks_variables,
    _reformat_date,
    _create_last_fight_variables,
    _create_home_variables,
    _birth_country,
)


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
