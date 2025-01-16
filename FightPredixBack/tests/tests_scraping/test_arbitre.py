"""Module de test pour la librairie de scraping des données de l'arbitrage"""

from FightPredixBack.FightPredixScraping.scraping.lib_arbitre import (
    _requete_arbitre,
    _creer_liste_arbitres,
)
import pytest
from bs4 import BeautifulSoup

from .fixtures import driver  # noqa F401


@pytest.fixture
def url_arbitre():
    return "https://www.ufc-fr.com/arbitre.html"


@pytest.fixture
def soup_arbitres(driver, url_arbitre):  # noqa F811
    """
    Fonction qui permet de récupérer la page d'un arbitre
    """

    driver.get(url_arbitre)
    return BeautifulSoup(driver.page_source, "html.parser")


def test_requete_arbitre(driver, url_arbitre):  # noqa F811
    """
    On vérifie que la fonction _requete_arbitre renvoie bien une page
    """
    driver.get(url_arbitre)
    assert driver.current_url == url_arbitre
    assert isinstance(_requete_arbitre(driver=driver, url=url_arbitre), BeautifulSoup)


def test_creer_liste_arbitres(soup_arbitres):
    """
    On vérifie que la fonction _creer_liste_arbitres renvoie bien une liste de dictionnaires
    """

    liste_arbitres = _creer_liste_arbitres(soup_arbitres)
    assert isinstance(liste_arbitres, dict)
    assert len(liste_arbitres["Rang"]) > 0
    assert len(liste_arbitres["photo"]) > 0
    assert len(liste_arbitres["Nom"]) > 0
    assert len(liste_arbitres["Total_combats_ufc"]) > 0
    assert len(liste_arbitres["liens"]) > 0

    for rang, photo, nom, total_combats_ufc, liens in zip(
        liste_arbitres["Rang"],
        liste_arbitres["photo"],
        liste_arbitres["Nom"],
        liste_arbitres["Total_combats_ufc"],
        liste_arbitres["liens"],
    ):
        assert isinstance(rang, str)
        assert isinstance(photo, str)
        assert isinstance(nom, str)
        assert isinstance(total_combats_ufc, str)
        assert isinstance(liens, str)
        assert "https" in liens
        assert "ufc-fr.com" in liens
        assert "/arbitre" in liens

    assert "Herb Dean" in liste_arbitres["Nom"]
    assert "Mike Beltran" in liste_arbitres["Nom"]
    assert "Osiris Maia" in liste_arbitres["Nom"]
