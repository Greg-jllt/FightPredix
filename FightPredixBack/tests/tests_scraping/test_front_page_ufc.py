"""Module de test pour la librairie lib_front_page.py"""

import pandas as pd
from FightPredixBack.FightPredixScraping.lib_front_page_ufc import (
    _recolte_pages_combattants,
    _deja_present,
)
from bs4 import BeautifulSoup
from .fixtures import driver, url, url_combattant


def test_requete_page_souhaitee(driver, url):
    """
    On vérifie que la page souhaitée a bien été atteinte
    """

    driver.get(url)
    assert driver.current_url == url


def test_recolte_pages_combattants(driver, url):
    """
    On vérifie que la fonction _recolte_pages_combattants renvoie bien une liste de liens
    """

    driver.get(url)

    liste_liens = _recolte_pages_combattants(driver)
    assert isinstance(liste_liens, list)
    for liens in liste_liens:
        assert isinstance(liens, str)
        assert "https" in liens
        assert "ufc.com" in liens
        assert "/athlete/" in liens
        assert " " not in liens


def test_deja_presents():
    """
    On vérifie que la fonction _deja_present renvoie bien True si l'élément est déjà présent
    """

    Data = pd.DataFrame({"NAME": ["jean jean"]})

    assert _deja_present(Data, "https://www.ufc.com/athlete/jean-jean")
    assert not _deja_present(Data, "https://www.ufc.com/athlete/alfrd-alfred")


def test_url_combattant_souhaitee(driver, url_combattant):
    """
    On vérifie que l'url du combattant souhaité est bien atteinte
    """

    driver.get(url_combattant)
    assert driver.current_url == url_combattant
