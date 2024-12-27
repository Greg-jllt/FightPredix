from .lib_front_page import _page_principal_UFC
from .lib_combats import _main_combat_recolte
from .lib_ufc_stats import _cherche_combattant_UFC_stats
from .lib_constructeur import _difference_combats, _age_by_DOB

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

import pandas as pd

def Dataframe_caracteristiques(driver: webdriver.Chrome) -> pd.DataFrame:

    Data = _page_principal_UFC(main_driver=driver)

    return  Data


def Dataframe_caracteristiques_ufc_stats(data: pd.DataFrame, driver: webdriver.Chrome) -> pd.DataFrame:
    
    Data = _cherche_combattant_UFC_stats(data=data, driver=driver)

    Data.to_csv("FightPredixApp/Data/Data_ufc_fighters.csv", index=False)

    return Data


def Dataframe_combats(driver: webdriver.Chrome) -> pd.DataFrame:

    Data = _main_combat_recolte(driver=driver)

    return Data


def _constructeur(Data: pd.DataFrame, combats: pd.DataFrame) -> pd.DataFrame:

    Data = _age_by_DOB(Data)

    combats = _difference_combats(Data, combats)

    return combats

def main():

    chrome_options = Options()
    
    chrome_options.add_argument("--headless")

    main_driver = webdriver.Chrome(options=chrome_options)

    Data = Dataframe_caracteristiques(main_driver)

    main_driver = webdriver.Chrome(options=chrome_options)

    Data = Dataframe_caracteristiques_ufc_stats(Data,main_driver)

    Data = Dataframe_combats(main_driver)

    main_driver.quit()

    combats = _constructeur(Data, Data)

    combats.to_csv("FightPredixApp/Data/Data_ufc_combats.csv", index=False)

    return 

if __name__ == "__main__":

    main()
