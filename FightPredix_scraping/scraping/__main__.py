"""
Processus de scraping des données sur les sites UFC.com, UFC stats et Tapology.
Construction de la base de données récapitulant les combats de l'UFC et les informations des combattants.
"""

from .lib_front_page import _page_principal_UFC
from .lib_combats import _main_combat_recolte
from .lib_ufc_stats import _cherche_combattant_UFC_stats, _ratrappage_manquants
from .lib_constructeur import _main_construct, _derniere_difference
from .lib_join_ufc_tapology import _main_tapology
from .lib_arbitre import _main_arbitre
from .outils import configure_logger
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import polars as pl
import pandas as pd
import os


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_scraping")


def Dataframe_caracteristiques(driver: webdriver.Chrome) -> pd.DataFrame:
    Data = _page_principal_UFC(main_driver=driver)

    return Data


def Dataframe_caracteristiques_ufc_stats(
    data: pd.DataFrame, driver: webdriver.Chrome
) -> pd.DataFrame:
    Data = _cherche_combattant_UFC_stats(data=data, driver=driver)

    return Data


def Dataframe_combats(driver: webdriver.Chrome) -> pd.DataFrame:
    Data = _main_combat_recolte(driver=driver)

    return Data


def _constructeur(
    combats: pd.DataFrame, Data: pd.DataFrame, main_driver: webdriver.Chrome
) -> pd.DataFrame:
    Data = _ratrappage_manquants(combats, Data, main_driver)
    combats, Data = _main_construct(combats, Data)

    return combats, Data


def _join_arbitre(combats: pd.DataFrame, data_arbitres: pd.DataFrame) -> pl.DataFrame:
    data_arbitres.rename(columns={"Nom": "Arbitre"}, inplace=True)
    combats.rename(columns={"Referee": "Arbitre"}, inplace=True)
    return (
        pl.DataFrame(combats)
        .join(pl.DataFrame(data_arbitres), on="Arbitre", how="left")
        .drop(["Rang", "liens"])
    )


def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    main_driver = webdriver.Chrome(options=chrome_options)

    # logger.info("Lancement du scraping sur UFC.com")
    Data = Dataframe_caracteristiques(main_driver)

    main_driver.quit()

    main_driver = webdriver.Chrome(options=chrome_options)

    # Data = pd.read_csv("Data/Data_ufc_fighters.csv")

    logger.info("Lancement du scraping sur UFC stats")
    Data = Dataframe_caracteristiques_ufc_stats(Data, main_driver)
    # Data.to_csv("Data/Data_ufc_fighters.csv", index=False)

    logger.info("Lancement du scraping sur tapology et création des données jointes")
    Data = _main_tapology()
    # Data.to_pandas().to_csv("Data/Data_ufc_complet.csv", index=False)

    Data = pd.read_csv("Data/Data_ufc_complet.csv")

    logger.info("Lancement du scraping sur les combats")
    combats = Dataframe_combats(main_driver)
    # combats.to_csv("Data/Data_ufc_combats_simple.csv", index=False)

    main_driver.quit()

    # combats = pd.read_csv("Data/Data_ufc_combats_simple.csv")

    main_driver = webdriver.Chrome(options=chrome_options)

    logger.info("Scraping des données sur les arbitres sur UFC_fans")
    data_arbitres = _main_arbitre().to_pandas()
    combats = _join_arbitre(combats, data_arbitres).to_pandas()

    # combats.to_csv("Data/Data_ufc_combat_complet_arbitres.csv", index=False)

    logger.info("Construction des données finales")
    combats, Data = _constructeur(combats, Data, main_driver)
    # combats.to_csv("Data/Data_ufc_combat_complet_actuel_clean.csv", index=False)

    main_driver.quit()

    combats = _derniere_difference(combats, Data)

    Data.to_csv("Data/Data_final_fighters.csv", index=False)
    combats.to_csv("Data/Data_final_combats.csv", index=False)

    logger.info("Suppression des fichiers temporaires")
    for file_path in [
        "Data/Data_ufc_fighters.csv",
        "Data/Data_jointes_ufc_tapology",
        "Data/data_tapology.csv",
        "Data/Data_ufc_combat_complet_actuel_clean.csv",
        "Data/Data_ufc_combats_simple.csv",
        "Data/clean_tapology.csv",
    ]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Le fichier {file_path} a été supprimé avec succès.")
        else:
            print(f"Le fichier {file_path} n'existe pas.")


if __name__ == "__main__":
    main()
