"""Teste les fonctions de lib_characteristics_collection.py"""

import pandas as pd
import pytest
from FightPredix.lib_caracteristic_collector import (
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

from .fixtures import url_combattant, webdriver

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_infos_principal_combattant(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _infos_principal_combattant
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    dictio["NAME"] = webdriver.find_element(By.CSS_SELECTOR, "div.hero-profile > div.hero-profile__info > h1").text
    assert dictio["NAME"] == "DANNY ABBADI"

    _infos_principal_combattant(webdriver, dictio)

    assert dictio["WIN"] == 2
    assert dictio["LOSSES"] == 2
    assert dictio["DRAWS"] == 0
    assert dictio["DIVISION"] == "Lightweight Division"
    assert dictio["GENRE"] == "Male"


def test_combattant_actif(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _combattant_actif
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _combattant_actif(webdriver, dictio)
    assert dictio["Actif"] == False


def test_bio_combattant(webdriver,url_combattant):
    """
    Fonction qui teste la fonction _bio_combattant
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _bio_combattant(webdriver, dictio)

    assert dictio["ÂGE"] == 39.0
    assert dictio["LA TAILLE"] == 71.0
    assert dictio["POIDS"] == 156.0


def test_tenant_titre(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _tenant_titre
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _tenant_titre(webdriver, dictio)
    assert not dictio["Title_holder"]


def test_stats_combattants(webdriver,url_combattant):
    """
    Fonction qui teste la fonction _stats_combattant
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _stats_combattant(webdriver, dictio)

    assert dictio["PERMANENT"] is None
    assert dictio["CLINCH"] is None
    assert dictio["SOL"] is None
    assert dictio["KO/TKO"] is None
    assert dictio["DEC"] is None
    assert dictio["SUB"] is None


def test_stats_corps_combattant(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _stats_corps_combattant
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _stats_corps_combattant(webdriver, dictio)

    assert dictio["sig_str_head"] is None
    assert dictio["sig_str_body"] is None
    assert dictio["sig_str_leg"] is None


def test_pourcentage_touche_takedown(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _pourcentage_touche_takedown
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _pourcentage_touche_takedown(webdriver, dictio)

    assert dictio["PRÉCISION SAISISSANTE"] is None
    assert dictio["PRÉCISION DE TAKEDOWN"] is None


def test_mesures_combattant(webdriver, url_combattant):
    """
    Fonction qui teste la fonction _mesures_combattant
    """
    webdriver.get(url_combattant)
    dictio = defaultdict()
    _mesures_combattant(webdriver, dictio)

    assert dictio["SIG. STR. A ATTERRI"] is None
    assert dictio["SIG. FRAPPES ENCAISSÉES"] is None
    assert dictio["TAKEDOWN AVG"] is None
    assert dictio["ENVOI AVG"] is None
    assert dictio["SIG. STR.DÉFENSE"] is None
    assert dictio["DÉFENSE DE DÉMOLITION"] is None
    assert dictio["KNOCKDOWN AVG"] is None
    assert dictio["TEMPS DE COMBAT MOYEN"] is None
