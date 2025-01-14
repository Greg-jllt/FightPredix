"""
Module de test pour le module lib_tapology.py
"""

import pytest
from scraping.lib_scraping_tapology import (
    _connect_vpn,
    _disconnect_vpn,
    _recherche_nom,
    _explorer_combattant,
    _scraper_combattant,
    _procedure_de_scraping,
)
import json
import polars as pl
from .fixtures import driver
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def df():
    with open("./FightPredix_scraping/tests/data_test/data_tapology_test.json", 'r') as f:
        df = json.load(f)
    return pl.DataFrame(df)


@pytest.fixture
def driver_tapology(driver):
    driver.get("https://www.tapology.com")

    def finalizer():
        """
        teardown : ferme le navigateur à la fin du test afin de ne laisser aucune instance de navigateur ouverte
        """

        driver.close()
        driver.quit()

    return driver


def test_disconnect_vpn():
    """
    Test de la fonction _disconnect_vpn
    """
    try:
        _disconnect_vpn()
    except Exception as e:
        raise e


def test_connect_vpn():
    """
    Test de la fonction _connect_vpn
    """

    try:
        _connect_vpn()
    except Exception as e:
        raise e


def test_recherche_nom(driver_tapology):
    """
    Test de la fonction _recherche_nom
    """
    _recherche_nom("Conor McGregor", driver_tapology)


def test_explorer_combattant(driver_tapology):
    """
    Test de la fonction _explorer_combattant
    """

    driver_tapology = _recherche_nom("Conor McGregor", driver_tapology)
    assert _explorer_combattant(driver_tapology, "https://www.tapology.com")[1]

    driver_tapology = _recherche_nom("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ", driver_tapology)
    assert not _explorer_combattant(driver_tapology, "https://www.tapology.com")[1]


def test_scraper_combattant(df, driver_tapology):
    """
    Test de la fonction _scraper_combattant
    """

    with open("./FightPredix_scraping/tests/data_test/data_tapology_test.json", 'r') as f:
        liste_dictio = json.load(f)

    for nom in (df["NAME"][4], df["NAME"][0], df["NAME"][7]):
        sub_driver = _recherche_nom(nom, driver_tapology)
        sub_driver, combattant_trouvee = _explorer_combattant(
            sub_driver, "https://www.tapology.com"
        )
        assert combattant_trouvee

        dictio = _scraper_combattant(sub_driver, nom)

        assert dict(dictio[0]) in liste_dictio


def test_procedure_de_scraping(driver_tapology):
    """
    Test de la fonction _procedure_de_scraping
    """

    dictio, driver_tapology = _procedure_de_scraping(
        driver_tapology, "https://www.tapology.com", "Conor Mcgregor"
    )
    assert dictio

    dictio, driver_tapology = _procedure_de_scraping(
        driver_tapology, "https://www.tapology.com", "zzzzzzzzzzzzzz"
    )
    assert not dictio


{'NAME': 'Kevin Christian', 'Name:tapology': 'Kevin Christian', 'Nickname:tapology': 'N/A', 'Pro MMA Record:tapology': '9-2-0 (Win-Loss-Draw)', 'Current MMA Streak:tapology': '6 Wins', 'Age:tapology': '29', 'Height:tapology': '6\'7" (201cm)', 'Weight Class:tapology': 'Light Heavyweight', 'Affiliation:tapology': 'Cosme Junior Team', 'Last Fight:tapology': 'September 24, 2024\nin\nDWCS', 'Career Disclosed Earnings:tapology': '$0 USD', 'Born:tapology': 'Rio Preto da Eva, Amazonas, Brazil', 'Fighting out of:tapology': 'Rio Preto da Eva, Amazonas, Brazil'}
{'NAME': 'Kevin Christian', 'Name:tapology': 'Joe Evans', 'Nickname:tapology': 'N/A', 'Amateur MMA Record:tapology': '1-1-0 (Win-Loss-Draw)', 'Current MMA Streak:tapology': '1 Win', 'Age:tapology': '31', 'Height:tapology': '6\'0" (183cm)', 'Weight Class:tapology': 'Light Heavyweight', 'Affiliation:tapology': 'Team Pinurv', 'Last Fight:tapology': 'April 11, 2015\nin\nHGMMA', 'Career Disclosed Earnings:tapology': '$0 USD', 'Born:tapology': 'United States', 'Fighting out of:tapology': 'Schenectady, New York'}