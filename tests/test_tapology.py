"""
Module de test pour le module lib_tapology.py
"""

import pytest
from FightPredix.lib_tapology import (
    _recherche_nom,
    _cliquer_sur_combattant,
    _scraper_combattant,
)
import json
import polars as pl
from .fixtures import driver  # noqa
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def df():
    with open("data_scrapee/combattant_ufc_pour_test.json", "r") as f:
        df = json.load(f)
    return pl.DataFrame(df)


@pytest.fixture
def combattant_non_trouve():
    with open("data_scrapee/combattant_non_trouve_tapology_pour_test.json", "r") as f:
        combattant_non_trouve = json.load(f)
    return combattant_non_trouve


@pytest.fixture
def driver_tapology(driver):  # noqa
    driver.get("https://www.tapology.com")
    return driver


def test_recherche_nom(driver_tapology):
    """
    Test de la fonction _recherche_nom
    """
    try:
        _recherche_nom("Conor McGregor", driver_tapology)
    except Exception as e:
        raise e


def test_cliquer_sur_combattant(driver_tapology):
    """
    Test de la fonction _cliquer_sur_combattant
    """

    _recherche_nom("Conor McGregor", driver_tapology)
    driver_tapology.implicitly_wait(10)

    try:
        _cliquer_sur_combattant(driver_tapology)
    except Exception as e:
        raise e


def test_scraper_combattant(df, driver_tapology, combattant_non_trouve):
    """
    Test de la fonction _scraper_combattant
    """

    with open("data_scrapee/combattant_tapology_pour_test.json", "r") as f:
        dictio_test = json.load(f)

    for nom in (df["Name"][5], df["Name"][0], df["Name"][7]):
        try:
            _recherche_nom(nom, driver_tapology)
            driver_tapology.implicitly_wait(10)
            try:
                _cliquer_sur_combattant(driver_tapology)
                driver_tapology.implicitly_wait(10)
                dictio = _scraper_combattant(driver_tapology)
                assert dictio in dictio_test
            except Exception:
                assert nom in combattant_non_trouve
        except Exception as e:
            raise e
