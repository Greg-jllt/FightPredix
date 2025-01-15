"""Description:

Librairie qui permet de scrapper les données des arbitres de l'UFC

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import polars as pl
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


def _main_arbitre() -> pl.DataFrame:
    """
    Fonction principale qui permet de récupérer les données des arbitres
    """

    logger.info("Lancement du scraping des arbitres sur UFC_fans")
    chrome_options = Options()
    chrome_options.add_argument(
        "--headless"
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.ufc-fr.com/arbitre.html"
    soup = _requete_arbitre(driver, url)
    liste_arbitres = _creer_liste_arbitres(soup)
    return pl.DataFrame(liste_arbitres)


if __name__ == "__main__":

    _main_arbitre()
