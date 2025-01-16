"""Module de test pour la librairie lib_front_page.py"""

import pandas as pd
from FightPredixBack.FightPredixScraping.scraping.lib_front_page_ufc import (
    _recolte_pages_combattants,
    _deja_present,
    _click_chargement_plus,
)

from .fixtures import driver, url, url_combattant  # noqa F401


def test_requete_page_souhaitee(driver, url):  # noqa F811
    """
    On vérifie que la page souhaitée a bien été atteinte
    """

    driver.get(url)
    assert driver.current_url == url


def test_recolte_pages_combattants(driver, url):  # noqa F811
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


def test_url_combattant_souhaitee(driver, url_combattant):  # noqa F811
    """
    On vérifie que l'url du combattant souhaité est bien atteinte
    """

    driver.get(url_combattant)
    assert driver.current_url == url_combattant


def test_click_chargement_plus(driver):  # noqa F811
    """
    On vérifie que la fonction _click_chargement_plus fonctionne
    """

    driver.get("https://www.ufc.com/athletes/all")
    _click_chargement_plus(driver)
    _click_chargement_plus(driver)
    assert driver.current_url == "https://www.ufc.com/athletes/all"
