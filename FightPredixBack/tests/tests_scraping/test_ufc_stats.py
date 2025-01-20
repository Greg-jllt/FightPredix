"""Module de test pour la librairie lib_ufc_stats.py"""

from FightPredixBack.FightPredixScraping.lib_ufc_stats import (
    _recolte_ufc_stats,
    _recolte_victoires,
    _collecteur_finish,
    _traitement_metriques,
    _convertisseur_taille,
)
import numpy as np
from .fixtures import driver_ufc_stats as driver  # noqa F401


def test_recolte_ufc_stats(driver):  # noqa F811
    """
    Teste la fonction _recolte_ufc_stats
    """
    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")

    driver.implicitly_wait(50)
    stats = _recolte_ufc_stats(driver)

    assert stats["HEIGHT:"] == "6' 4\""
    assert stats["WEIGHT:"] == "248 lbs."
    assert stats["REACH:"] == '84"'
    assert stats["STANCE:"] == "Orthodox"
    assert stats["DOB:"] == "Jul 19, 1987"
    assert stats["SLpM:"] == "4.38"
    assert stats["Str. Acc.:"] == "58%"
    assert stats["SApM:"] == "2.24"
    assert stats["Str. Def:"] == "64%"
    assert stats["TD Avg.:"] == "1.89"
    assert stats["TD Acc.:"] == "45%"
    assert stats["TD Def.:"] == "95%"
    assert stats["Sub. Avg.:"] == "0.5"


def test_recolte_victoires(driver):  # noqa F811
    """
    Teste la fonction _recolte_victoires
    """
    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")
    driver.implicitly_wait(50)
    resultats = _recolte_victoires(driver)

    assert resultats[0] == 28  # type: ignore
    assert resultats[1] == 1  # type: ignore
    assert resultats[2] == 0  # type: ignore


def test_collecteur_finish(driver):  # noqa F811
    """
    Teste la fonction _collecteur_finish
    """
    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")
    driver.implicitly_wait(50)
    finishes = _collecteur_finish(driver)

    assert finishes["KO/TKO"] == 6
    assert finishes["SUB"] == 6
    assert finishes["DEC"] == 10


def test_traitement_metriques(driver):  # noqa F811
    win_draw_loss = np.array([22, 1, 0])
    dict_res = {
        "KO/TKO": 6,
        "SUB": 6,
        "DEC": 10,
        "WIN": 22,
        "LOSSES": 1,
        "DRAWS": 0,
        "WIN_HP": 6,
        "LOSSES_HP": 0,
        "DRAWS_HP": 0,
        "HEIGHT": 76,
        "WEIGHT": 248.0,
        "REACH": 84,
        "STANCE": "Orthodox",
        "DOB": "Jul 19, 1987",
        "SLpM": 4.38,
        "Str. Acc.": 0.58,
        "SApM": 2.24,
        "Str. Def": 0.64,
        "TD Avg.": 1.89,
        "TD Acc.": 0.45,
        "TD Def.": 0.95,
        "Sub. Avg.": 0.5,
    }
    driver.implicitly_wait(50)
    assert _traitement_metriques(driver, win_draw_loss) == dict_res  # type: ignore


def test_convertisseur_taille():
    """
    Teste la fonction _convertisseur_taille
    """

    assert _convertisseur_taille("6' 4\"") == 76
    assert _convertisseur_taille("5' 6\"") == 66
    assert _convertisseur_taille("5' 0\"") == 60
    assert _convertisseur_taille("6' 0\"") == 72
    assert _convertisseur_taille("5' 8\"") == 68
    assert _convertisseur_taille("5' 10\"") == 70
    assert _convertisseur_taille("5' 11\"") == 71
    assert _convertisseur_taille("6' 1\"") == 73
    assert _convertisseur_taille("6' 2\"") == 74
    assert _convertisseur_taille("6' 3\"") == 75
    assert _convertisseur_taille("6' 5\"") == 77
    assert _convertisseur_taille("6' 6\"") == 78
    assert _convertisseur_taille("6' 7\"") == 79
    assert _convertisseur_taille("6' 8\"") == 80
    assert _convertisseur_taille("6' 9\"") == 81
    assert _convertisseur_taille("6' 10\"") == 82
    assert _convertisseur_taille("6' 11\"") == 83
    assert _convertisseur_taille("7' 0\"") == 84
    assert _convertisseur_taille("7' 1\"") == 85
    assert _convertisseur_taille("7' 2\"") == 86
    assert _convertisseur_taille("7' 3\"") == 87
    assert _convertisseur_taille("7' 4\"") == 88
    assert _convertisseur_taille("7' 5\"") == 89
    assert _convertisseur_taille("7' 6\"") == 90
    assert _convertisseur_taille("7' 7\"") == 91
