"""
Librairie pour recolter les informations des combattants de l'UFC sur https://www.tapology.com

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import polars as pl
from rich.console import Console
from collections import defaultdict
import json
from selenium.webdriver.common.keys import Keys


def _recherche_nom(nom: str, driver: webdriver.Chrome) -> None:
    """
    Fonction qui recherche un combattant sur tapology
    """

    search_box = driver.find_element(By.XPATH, '//*[@id="siteSearch"]')
    search_box.send_keys(nom)
    search_box.send_keys(Keys.RETURN)
    driver.implicitly_wait(10)


def _cliquer_sur_combattant(driver: webdriver.Chrome) -> None:
    """
    Fonction qui clique sur le combattant dans la barre de recherche
    """

    driver.find_element(
        By.XPATH, '//*[@id="content"]/div[2]/table/tbody/tr[2]/td[1]/a'
    ).click()
    driver.implicitly_wait(10)


def _scraper_combattant(driver: webdriver.Chrome) -> defaultdict:
    """
    Fonction qui recolte les informations d'un combattant sur tapology
    """

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tableau = soup.find("div", attrs={"id": "standardDetails"})
    ligne = tableau.find_all("div")
    dictio: defaultdict = defaultdict()
    for cellule in ligne:
        var = cellule.find("strong")
        value = cellule.find("span")
        if var and value:
            dictio[var.text.strip() + "tapology"] = value.text.strip()
    return dictio


if __name__ == "__main__":
    console = Console()
    with open("data_scrapee/combattant_ufc.json", "r") as f:
        df = json.load(f)

    df = pl.DataFrame(df)
    driver = webdriver.Chrome()
    url = "https://www.tapology.com"
    driver.get(url)

    driver.implicitly_wait(10)

    liste_dictio = []
    liste_combattant_non_trouve = []

    for nom in df["Name"]:
        _recherche_nom(nom, driver)
        driver.implicitly_wait(10)
        try:
            _cliquer_sur_combattant(driver)
            driver.implicitly_wait(10)
            dictio = _scraper_combattant(driver)
            liste_dictio.append(dictio)
        except Exception:
            liste_combattant_non_trouve.append(nom)

    driver.quit()

    with open("data_scrapee/combattant_tapology.json", "w") as f:
        json.dump(liste_dictio, f)

    with open("data_scrapee/combattant_non_trouve_tapology.json", "w") as f:
        json.dump(liste_combattant_non_trouve, f)

    console.print(f"Combattant(e)s non trouvé(e)s: {liste_combattant_non_trouve}")
