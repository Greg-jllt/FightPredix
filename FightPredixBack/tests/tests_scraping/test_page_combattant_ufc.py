"""Module de test les fonctions de lib_page_combattant_ufc.py"""

from FightPredixBack.FightPredixScraping.lib_page_combattant_ufc import (
    _infos_principal_combattant,
    _combattant_actif,
    _bio_combattant,
    _tenant_titre,
    _stats_combattant,
    _stats_corps_combattant,
    _pourcentage_touche_takedown,
    _mesures_combattant,
)
from collections import defaultdict
from selenium.webdriver.common.by import By

from .fixtures import url_combattant, driver  # noqa F401


def test_infos_principal_combattant(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _infos_principal_combattant
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    dictio["NAME"] = driver.find_element(
        By.CSS_SELECTOR, "div.hero-profile > div.hero-profile__info > h1"
    ).text
    assert dictio["NAME"] == "JON JONES"

    _infos_principal_combattant(driver, dictio)
    assert dictio["WIN"] == 28
    assert dictio["LOSSES"] == 1
    assert dictio["DRAWS"] == 0
    assert dictio["GENRE"] == "Male"


def test_combattant_actif(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _combattant_actif
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _combattant_actif(driver, dictio)
    assert dictio["Actif"]


def test_bio_combattant(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _bio_combattant
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _bio_combattant(driver, dictio)

    assert dictio["ÂGE"] == 37.0
    assert dictio["LA TAILLE"] == 76.0
    assert dictio["POIDS"] == 237.6


def test_tenant_titre(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _tenant_titre
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _tenant_titre(driver, dictio)
    assert dictio["Title_holder"]


def test_stats_combattants(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _stats_combattant
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _stats_combattant(driver, dictio)

    assert dictio["PERMANENT"] == 1012
    assert dictio["CLINCH"] == 250
    assert dictio["SOL"] == 302
    assert dictio["KO/TKO"] == 11
    assert dictio["DEC"] == 10
    assert dictio["SUB"] == 7


def test_stats_corps_combattant(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _stats_corps_combattant
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _stats_corps_combattant(driver, dictio)

    assert dictio["sig_str_head"] == 759
    assert dictio["sig_str_body"] == 375
    assert dictio["sig_str_leg"] == 430


def test_pourcentage_touche_takedown(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _pourcentage_touche_takedown
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _pourcentage_touche_takedown(driver, dictio)
    assert dictio["PRÉCISION SAISISSANTE"] == 0.59
    assert dictio["PRÉCISION DE TAKEDOWN"] == 0.46


def test_mesures_combattant(driver, url_combattant):  # noqa F811
    """
    Fonction qui teste la fonction _mesures_combattant
    """
    driver.get(url_combattant)
    dictio = defaultdict()
    _mesures_combattant(driver, dictio)

    assert dictio["SIG. STR. A ATTERRI"] == 4.38
    assert dictio["SIG. FRAPPES ENCAISSÉES"] == 2.24
    assert dictio["TAKEDOWN AVG"] == 1.89
    assert dictio["ENVOI AVG"] == 0.46
    assert dictio["SIG. STR.DÉFENSE"] == 0.64
    assert dictio["DÉFENSE DE DÉMOLITION"] == 0.95
    assert dictio["KNOCKDOWN AVG"] == 0.25
    assert dictio["TEMPS DE COMBAT MOYEN"] == 892
