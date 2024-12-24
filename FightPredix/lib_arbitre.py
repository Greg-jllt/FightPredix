"""Description:

Librairie qui permet de scrapper les données des arbitres de l'UFC

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import json
from typing import Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
import logging


def _requete_arbitre(driver: webdriver.Chrome, url: str) -> BeautifulSoup:
    """
    Fonction qui permet de récupérer la page d'un arbitre
    """
    driver.get(url)
    time.sleep(2)

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
    lignes = (
        soup.find("table")
        .find("td", class_="tableau-gauche bg-tableau-defaut")
        .find_all("tr")
    )

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

    logging.info("Données générales des arbitres récupérées")
    return listes_combats


def _donnees_arbitres(driver: webdriver.Chrome, url: str) -> list[dict[str, list[str]]]:
    """
    Fonction qui permet de récupérer les données des arbitres
    """
    soup = _requete_arbitre(driver, url)
    liste_donnees_sur_arbitres: list[dict[str, list[str]]] = list()
    liste_arbitres = _creer_liste_arbitres(soup)

    for url in liste_arbitres["liens"]:
        logging.info(f"Récupération des données de l'arbitre: {url}")
        liste_donnees_sur_arbitres.append(_recup_donnees_arbitres(driver, url))
        logging.info(f"Données de l'arbitre récupérées: {url}")
        time.sleep(random.random(1, 5))
    return liste_donnees_sur_arbitres


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


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    driver = webdriver.Chrome(options=chrome_options)
    soup = _requete_arbitre(driver, "https://www.ufc-fr.com/arbitre.html")
    url = "https://www.ufc-fr.com/arbitre.html"
    with open("donnees_arbitres.json", "w") as f:
        json.dump(_mise_en_commun(driver, url), f, indent=4)

    logging.info("Scraping terminé")
    driver.quit()
