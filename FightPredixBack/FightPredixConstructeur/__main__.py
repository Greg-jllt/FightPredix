"""
Module principal de construction des nouvelles variables
"""

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd

from .lib_constructeur import _main_constructeur
from FightPredixBack.FightPredixScraping.scraping.lib_ufc_stats import (
    _ratrappage_manquants,
)
from .lib_nettoyage_avant_preprocess import (
    _main_nettoyage_avant_preprocess,
)


def _constructeur(
    combats: pd.DataFrame, Data: pd.DataFrame, main_driver: webdriver.Chrome
) -> pd.DataFrame:
    Data = _ratrappage_manquants(combats, Data, main_driver)
    combats, Data = _main_constructeur(combats, Data)
    combats = _main_nettoyage_avant_preprocess(combats)
    return combats, Data


if __name__ == "__main__":

    Data = pd.read_json("FightPredixBack/Data/Data_ufc_combattant_complet.json")
    combats = pd.read_json("FightPredixBack/Data/Data_ufc_combats_complet.json")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    main_driver = webdriver.Chrome(options=chrome_options)

    combats, Data = _constructeur(combats, Data, main_driver)

    main_driver.quit()

    Data.to_json("FightPredixApp/DataApp/Data_final_fighters.json")
    combats.to_json("FightPredixApp/DataApp/Data_final_combats.json")
    combats.to_json("FightPredixBack/Data/Data_final_combats.json")
