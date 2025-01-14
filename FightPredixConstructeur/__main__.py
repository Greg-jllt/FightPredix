"""
Module principal de construction des nouvelles variables
"""

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import pandas as pd

from .lib_constructeur import _main_constructeur
from FightPredixScraping.scraping.lib_ufc_stats import _ratrappage_manquants
from FightPredixScraping.scraping.__main__ import main as _main_recolte


def _constructeur(
    combats: pd.DataFrame, Data: pd.DataFrame, main_driver: webdriver.Chrome
) -> pd.DataFrame:
    Data = _ratrappage_manquants(combats, Data, main_driver)
    combats, Data = _main_constructeur(combats, Data)

    return combats, Data


_main_recolte()

Data = pd.read_json("Data/Data_ufc_combattant_complet.json")
combats = pd.read_csv("Data/Data_ufc_combats_complet.json")

chrome_options = Options()
chrome_options.add_argument("--headless")
main_driver = webdriver.Chrome(options=chrome_options)

combats, Data = _constructeur(combats, Data, main_driver)

combats.to_json("Data/Data_ufc_combats_complet.json")
main_driver.quit()

Data.to_json("FightPredixApp/Data/Data_final_fighters.json")
combats.to_json("FightPredixApp/Data/Data_final_combats.json")