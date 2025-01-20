"""Module de test pour la librairie lib_tapology.py"""

import pytest
from FightPredixBack.FightPredixScraping.lib_scraping_tapology import (
    _connect_vpn,
    _disconnect_vpn,
    _recherche_nom,
    _explorer_combattant,
    _scraper_combattant,
    _procedure_de_scraping,
)
from selenium.webdriver.chrome.options import Options
import json
import polars as pl
from .fixtures import driver  # noqa F401


@pytest.fixture
def df():
    with open(
        "FightPredixBack/tests/tests_scraping/data_test/data_tapology_test.json", "r"
    ) as f:
        df = json.load(f)
    return pl.DataFrame(df)


@pytest.fixture
def driver_tapology(driver): # noqa F811
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
    _recherche_nom(
        "Conor McGregor", driver_tapology, Options(), "https://www.tapology.com/"
    )


def test_explorer_combattant(driver_tapology):
    """
    Test de la fonction _explorer_combattant
    """

    driver_tapology = _recherche_nom(
        "Conor McGregor", driver_tapology, Options(), "https://www.tapology.com/"
    )
    assert _explorer_combattant(
        driver_tapology, "https://www.tapology.com", Options(), "Conor McGregor"
    )[1]

    driver_tapology = _recherche_nom(
        "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",
        driver_tapology,
        Options(),
        "https://www.tapology.com",
    )
    assert not _explorer_combattant(
        driver_tapology,
        "https://www.tapology.com",
        Options(),
        "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",
    )[1]



def test_procedure_de_scraping(driver_tapology):
    """
    Test de la fonction _procedure_de_scraping
    """

    dictio, driver_tapology = _procedure_de_scraping(
        driver_tapology,
        "https://www.tapology.com",
        "Conor Mcgregor",
        Options(),
    )

    assert dictio

    dictio, driver_tapology = _procedure_de_scraping(
        driver_tapology,
        "https://www.tapology.com",
        "zzzzzzzzzzzzzz",
        Options(),
    )
    assert not dictio
