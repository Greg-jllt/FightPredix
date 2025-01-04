"""Description:

Librairie qui permet de scrapper les données des arbitres de l'UFC

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from typing import Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import logging
import polars as pl
from streamlit import success
from .lib_scraping_tapology import _restart_with_new_vpn
from .outils import configure_logger
from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_arbitre")


def _requete_arbitre(driver: webdriver.Chrome, url: str) -> BeautifulSoup:
    """
    Fonction qui permet de récupérer la page d'un arbitre
    """
    driver.get(url)
    driver.implicitly_wait(10)

    return BeautifulSoup(driver.page_source, "html.parser")


def _creer_liste_arbitres(soup: BeautifulSoup) -> dict[str, list[str]]:
    """
    Fonction qui permet de récupérer la liste des arbitres
    """
    liste_arbitres: dict = dict(
        Rang=list(),
        photo=list(),
        Nom=list(),
        Total_combats_ufc=list(),
        liens=list(),
        historique=list(),
    )

    lignes = (
        soup.find(class_="tableau-gauche bg-tableau-defaut")
        .find(class_="bloc")
        .find_all("tr")
    )

    for ligne in lignes:
        elements = ligne.find_all("td")
        liste_arbitres["Rang"].append(elements[0].text.strip())
        liste_arbitres["photo"].append(
            "https://www.ufc-fr.com" + elements[1].find("img")["src"]
        )
        liste_arbitres["Nom"].append(elements[2].text.strip())
        liste_arbitres["Total_combats_ufc"].append(elements[3].text.strip())
        liste_arbitres["liens"].append(
            "https://www.ufc-fr.com/" + elements[2].find("a", href=True)["href"]
        )

    return liste_arbitres


def _recup_donnees_arbitres(
    driver: webdriver.Chrome, url_arbitre: str
) -> dict[str, list[str]]:
    """
    Fonction qui permet de récupérer les données des arbitres
    """
    driver.get(url_arbitre)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    logging.info(f"Récupération des données général des arbitres: {url_arbitre}")
    if soup.find("table") is None:
        logging.info("Pas de données générales pour cet arbitre")
        return dict()
    else:
        lignes = soup.find("table")
        lignes = lignes.find("td", class_="tableau-gauche bg-tableau-defaut")
        lignes = lignes.find_all("tr")

        listes_combats: dict = dict(
            Date=list(),
            Evenement=list(),
            Vainqueur=list(),
            Combattant1=list(),
            Combattant2=list(),
        )

        for ligne in lignes:
            elements = ligne.find_all("td")
            listes_combats["Date"].append(elements[0].text.strip())
            listes_combats["Evenement"].append(elements[1].text.strip())
            if elements[2].text.strip() == "LOSS":
                listes_combats["Vainqueur"].append(elements[5].text.strip())
            elif elements[2].text.strip() == "WIN":
                listes_combats["Vainqueur"].append(elements[3].text.strip())
            else:
                listes_combats["Vainqueur"].append("Match nul")
            listes_combats["Combattant1"].append(elements[3].text.strip())
            listes_combats["Combattant2"].append(elements[5].text.strip())
            listes_combats["arbitre"] = (
                soup.find("table")
                .find("td", class_="tableau-gauche bg-tableau-defaut")
                .find("div", class_="titre")
                .text.split(":")[1]
                .strip()
            )

        logging.info("Données générales des arbitres récupérées")
        return listes_combats


def _donnees_arbitres(driver: webdriver.Chrome, url: str) -> list[dict[str, list[str]]]:
    """
    Fonction qui permet de récupérer les données des arbitres
    """
    soup = _requete_arbitre(driver, url)
    liste_donnees_sur_arbitres: list[dict[str, list[str]]] = list()
    driver.implicitly_wait(10)
    liste_arbitres = _creer_liste_arbitres(soup)
    while True:
        try:
            for url in liste_arbitres["liens"]:
                driver.implicitly_wait(50)
                logging.info(f"Récupération des données de l'arbitre: {url}")
                liste_donnees_sur_arbitres.append(_recup_donnees_arbitres(driver, url))
                logging.info(f"Données de l'arbitre récupérées: {url}")
                driver.implicitly_wait(10)
            return liste_donnees_sur_arbitres
        except WebDriverException as e:
            logger.error(f"Erreur lors du scraping des arbitres: {e}")
            driver = _restart_with_new_vpn(driver, url=url, options=Options())
            logger.info("Relance du scraping avec un nouveau VPN")


def _mise_en_commun(driver: webdriver.Chrome, url) -> dict[str, Any]:
    """
    Fonction qui permet de mettre en commun toutes les données des arbitres
    """

    liste_arbitres: dict[str, Any]
    liste_arbitres = _creer_liste_arbitres(_requete_arbitre(driver, url))
    liste_arbitres["historique"] = list()
    donnees_arbitres = _donnees_arbitres(driver, url)

    for donnees in donnees_arbitres:
        liste_arbitres["historique"].append(donnees)  # type: ignore

    return liste_arbitres


def _create_data_combats_arbitre(data: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui permet de créer un DataFrame à partir des données des combats des arbitres
    """

    liste_df_hist = []
    for hist in data["historique"]:
        df_hist = pl.DataFrame(hist)
        liste_df_hist.append(df_hist)
    data_hist = pl.concat(liste_df_hist)

    return data_hist


def _create_data_arbitres(df_histo: pl.DataFrame, data: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui permet de créer un DataFrame à partir des données des arbitres
    """

    data = data.to_pandas()
    liste_photo = []
    liste_total_match = []
    try:
        for nom in df_histo["arbitre"]:
            logger.info(f"Récupération de la photo de l'arbitre {nom}")
            liste_photo.append(data[data["Nom"] == nom]["photo"].values[0])
            liste_total_match.append(
                data[data["Nom"] == nom]["Total_combats_ufc"].values[0]
            )
    except IndexError:
        logger.info(f"L'arbitre {nom} n'a pas de photo")
        liste_photo.append(None)
        liste_total_match.append(None)

    df_histo = df_histo.with_columns(
        pl.Series("photo_arbitre", liste_photo),
        pl.Series("Total_combats_ufc_arbitre", liste_total_match),
    )

    return df_histo


if __name__ == "__main__":
    success = False
    while not success:
        try:
            logger.info("Lancement du scraping des arbitres sur UFC_fans")
            chrome_options = Options()
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(options=chrome_options)
            soup = _requete_arbitre(driver, "https://www.ufc-fr.com/arbitre.html")
            url = "https://www.ufc-fr.com/arbitre.html"

            logger.info("Création du DataFrame des arbitres")
            data = pl.DataFrame(_mise_en_commun(driver, url))
            data_hist = _create_data_combats_arbitre(data)
            data_arbitres = _create_data_arbitres(data_hist, data)
            data_arbitres.to_pandas().to_csv("data/Data_arbitres.csv", index=False)
            logging.info("Scraping terminé")
            driver.quit()
            success = True
        except WebDriverException as e:
            logger.error(f"Erreur lors du scraping des arbitres: {e}")
            driver = _restart_with_new_vpn(driver, url=url, options=chrome_options)
            logger.info("Relance du scraping avec un nouveau VPN")
