"""Teste les fonctions de lib_front_page.py"""

import os
import sys
import pandas as pd

# import pytest
from FightPredix.lib_front_page import _recolte_pages_combattants, _deja_present
from bs4 import BeautifulSoup


from .fixtures import driver, url, url_combattant  # noqa: F401

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_requete_page_souhaitee(driver, url):  # noqa: F811
    """
    On vérifie que la page souhaitée a bien été atteinte
    """

    driver.get(url)
    assert driver.current_url == url


def test_recolte_pages_combattants(driver, url):  # noqa: F811
    """
    On vérifie que la fonction _recolte_pages_combattants renvoie bien une liste de liens
    """

    driver.get(url)

    front_content = driver.page_source

    front_soup = BeautifulSoup(front_content, "html.parser")

    liste_liens = _recolte_pages_combattants(front_soup)
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

    Data = pd.DataFrame({"Name": ["jean jean"]})

    assert _deja_present(Data, "https://www.ufc.com/athlete/jean-jean")
    assert not _deja_present(Data, "https://www.ufc.com/athlete/alfrd-alfred")


def test_url_combattant_souhaitee(driver, url_combattant):  # noqa: F811
    """
    On vérifie que l'url du combattant souhaité est bien atteinte
    """

    driver.get(url_combattant)
    assert driver.current_url == url_combattant
