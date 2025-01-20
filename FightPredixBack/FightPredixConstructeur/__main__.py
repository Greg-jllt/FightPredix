"""
Module principal de construction des nouvelles variables
"""

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd
from FightPredixBack.FightPredixScraping.lib_ufc_stats import _ratrappage_manquants
from FightPredixBack.FightPredixConstructeur.lib_constructeur import _main_constructeur
from FightPredixBack.FightPredixConstructeur.lib_nettoyage_avant_preprocess import (
    _main_nettoyage_avant_preprocess,
)
from datetime import datetime
from FightPredixBack.outils import configure_logger


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_constructeur")


def _constructeur(
    combats: pd.DataFrame, Data: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    combats, Data = _main_constructeur(combats, Data)
    combats = _main_nettoyage_avant_preprocess(combats)
    return combats, Data


if __name__ == "__main__":

    Data = pd.read_json("FightPredixBack/Data/Data_ufc_combattant_complet.json")
    combats = pd.read_json("FightPredixBack/Data/Data_ufc_combats_complet.json")

    combats, Data = _constructeur(combats, Data)

    Data.to_json("FightPredixApp/DataApp/Data_final_fighters.json", orient="records")
    combats.to_json("FightPredixApp/DataApp/Data_final_combats.json", orient="records")
