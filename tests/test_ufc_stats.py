"""Teste les fonctions de lib_ufc_stats.py"""

import pandas as pd
import pytest

from FightPredix.lib_ufc_stats import (
    _recolte_ufc_stats,
    _recolte_victoires,
    _collecteur_finish,
    _traitement_metriques,

)

from .fixtures import driver_ufc_stats as driver 

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_recolte_ufc_stats(driver):

    driver.get("http://www.ufcstats.com/fighter-details/07f72a2a7591b409")

    stats = _recolte_ufc_stats(driver)

    assert stats["HEIGHT:"] == "6' 4\""
    assert stats["WEIGHT:"] == "248 lbs."
    assert stats["REACH:"] == "84\""
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

    resultats = _recolte_victoires(driver)

    assert resultats[0] == 28
    assert resultats[1] == 1
    assert resultats[2] == 0


def test_collecteur_finish(driver):

    finishes = _collecteur_finish(driver)

    assert finishes["KO/TKO"] == 6
    assert finishes["SUB"] == 6
    assert finishes["DEC"] == 10

def test_traitement_metriques(driver):
    dict_res = {'KO/TKO': 6,
    'SUB': 6,
    'DEC': 10,
    'Win': 28,
    'Losses': 1,
    'Draws': 0,
    'HEIGHT': 76,
    'WEIGHT': 248.0,
    'REACH': 84,
    'STANCE': 'Orthodox',
    'DOB': 'Jul 19, 1987',
    'SLpM': 4.38,
    'Str. Acc.': 0.58,
    'SApM': 2.24,
    'Str. Def': 0.64,
    'TD Avg.': 1.89,
    'TD Acc.': 0.45,
    'TD Def.': 0.95,
    'Sub. Avg.': 0.5}

    assert _traitement_metriques(driver) == dict_res


