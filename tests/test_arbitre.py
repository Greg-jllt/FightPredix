"""Description

Module de test pour la librairie de scraping des données de l'arbitrage
"""

import requests_cache
from FightPredix.lib_arbitre import (
    _requete_arbitre,
    _creer_liste_arbitres,
    _recup_donnees_arbitres,
    _donnees_arbitres,
    _mise_en_commun,
)
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pytest
import os
import sys
import time

from .fixtures import driver

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

requests_cache.install_cache("cache_test_arbitre")


@pytest.fixture
def url_arbitre():
    return "https://www.ufc-fr.com/arbitre.html"


@pytest.fixture
def soup_arbitres(driver, url_arbitre):
    """
    Fonction qui permet de récupérer la page d'un arbitre
    """

    driver.get(url_arbitre)
    time.sleep(2)
    try:
        consent_button = driver.find_element(By.ID, "cmpbntnotxt")
        consent_button.click()
    except Exception:
        print("Bouton de consentement non trouvé ou déjà cliqué.")
    return BeautifulSoup(driver.page_source, "html.parser")


@pytest.fixture
def accepter_cookies(driver):
    """
    Fonction qui permet d'accepter les cookies
    """

    driver.get("https://www.ufc-fr.com/arbitre-30.html")
    time.sleep(2)

    try:
        consent_button = driver.find_element(By.ID, "cmpbntnotxt")
        consent_button.click()
    except Exception:
        print("Bouton de consentement non trouvé ou déjà cliqué.")

    return driver


def test_requete_arbitre(driver, url_arbitre):
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


def test_recup_donnees_arbitres(driver, accepter_cookies):
    """
    Fonction qui teste la fonction _recup_donnees_arbitres
    """
    accepter_cookies
    liste_combats = _recup_donnees_arbitres(
        driver, "https://www.ufc-fr.com/arbitre-30.html"
    )

    assert isinstance(liste_combats, dict)
    assert len(liste_combats["Date"]) > 0
    assert "Charles Oliveira" in liste_combats["Vainqueur"]
    assert "UFC 244" in liste_combats["Evenement"]
    assert "Brad Tavares" not in liste_combats["Vainqueur"]


def test_donnees_arbitres(driver, url_arbitre):
    """
    Fonction qui teste la fonction _donnees_arbitres
    """

    donnees = _donnees_arbitres(driver, url_arbitre)

    assert isinstance(donnees[0], dict)
    assert len(donnees[0]["Date"]) > 0
    assert "Yana Santos" in donnees[0]["Vainqueur"]
    assert "UFC 302" in donnees[0]["Evenement"]
    assert "Claudio Puelles" not in donnees[0]["Vainqueur"]


def test_mise_en_commun(driver, url_arbitre):
    """
    Fonction qui teste la fonction _mise_en_commun
    """

    donnees = _mise_en_commun(driver, url_arbitre)

    assert isinstance(donnees, dict)
    assert len(donnees["Total_combats_ufc"]) > 0
    assert "Herb Dean" in donnees["Nom"]
    assert "Yana Santos" in donnees["historique"][0]["Vainqueur"]
    assert "UFC 302" in donnees["historique"][0]["Evenement"]
    assert "Claudio Puelles" not in donnees["historique"][0]["Vainqueur"]
    assert isinstance(donnees["historique"][0], dict)
