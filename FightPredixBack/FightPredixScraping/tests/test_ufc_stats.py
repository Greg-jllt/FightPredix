"""Module de test pour la librairie lib_ufc_stats.py"""

from scraping.lib_ufc_stats import (
    _recolte_ufc_stats,
    _recolte_victoires,
    _collecteur_finish,
    _traitement_metriques,
    _vic_draws_losses_autres_parcours,
)
import numpy as np
from .fixtures import driver_ufc_stats as driver
import os
import numpy as np
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_recolte_ufc_stats(driver):
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


def test_recolte_victoires(driver):
    """
    Teste la fonction _recolte_victoires
    """
    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")
    driver.implicitly_wait(50)
    resultats = _recolte_victoires(driver)

    assert resultats[0] == 28
    assert resultats[1] == 1
    assert resultats[2] == 0


def test_collecteur_finish(driver):
    """
    Teste la fonction _collecteur_finish
    """
    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")
    driver.implicitly_wait(50)
    finishes = _collecteur_finish(driver)

    assert finishes["KO/TKO"] == 6
    assert finishes["SUB"] == 6
    assert finishes["DEC"] == 10


def test_traitement_metriques(driver):

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
    assert _traitement_metriques(driver, win_draw_loss) == dict_res
