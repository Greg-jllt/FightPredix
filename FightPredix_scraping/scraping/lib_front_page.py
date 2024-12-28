"""
Librairie pour recolter les informations des combattants de l'UFC à partir de ufc.com

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from collections import defaultdict
import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from rich.console import Console
from .lib_caracteristic_collector import _extraire_info_combattant
from typing import Any
from datetime import datetime

import re
import time
import pandas as pd

from .outils import configure_logger


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_UFC_main")


def _recolte_pages_combattants(driver) -> list:
    """
    Fonction qui recolte les liens des combattants sur une page
    """
    elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/athlete/") and contains(@class, "e-button--black")]')

    motif = re.compile(r"/athlete/[\w]+-[\w]+")

    hrefs = [element.get_attribute('href') for element in elements if motif.search(element.get_attribute('href'))]

    return hrefs


def _visite_page_combattant(
    driver: webdriver.Chrome, url: str
) -> defaultdict:
    """
    Fonction qui visite la page d'un combattant et recolte ses informations
    """

    driver.get(url)
    time.sleep(1)

    dictio = _extraire_info_combattant(driver)
    logger.info(dictio)
    return dictio


def _click_chargement_plus(main_driver: webdriver.Chrome) -> None:
    """
    Fonction qui clique sur le bouton de chargement plus d'elements
    """

    element = WebDriverWait(main_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@title='Load more items']"))
    )

    main_driver.execute_script("arguments[0].scrollIntoView(true);", element)

    time.sleep(1)

    actions = ActionChains(main_driver)
    actions.move_to_element(element).click().perform()

    time.sleep(2)


def _deja_present(data: pd.DataFrame, url: str) -> bool:
    """
    Fonction qui verifie si un combattant est deja present dans la base de donnees
    """

    pattern = re.compile(r"/athlete/([\w]+-[\w]+)")
    match = pattern.search(url)  # type: ignore
    if match:
        nom = match.group(1).replace("-", " ")
    else:
        nom = ""
    if nom in data["NAME"].values:
        return True
    return False


def _page_principal_UFC(
    main_driver: webdriver.Chrome, Data: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Fonction permettant de recolter les informations des combattants de l'UFC

    Args:
        main_driver (webdriver): Objet webdriver de la page principale
        Data (pd.Dataframe, optional): Dataframe contenant les informations des combattants deja recoltees. None par default.
        essais (int, optional): Nombre de tentatives. None par default.

    Returns:
        pd.Dataframe: Dataframe contenant les informations des combattants
    """

    result: list[Any] = list()
    hrefs = list()
    
    main_driver.get("https://www.ufc.com/athletes/all?filters%5B0%5D=status%3A23")

    if Data is None:
        Data = pd.DataFrame(columns=["NAME"])

    def _page_principal_sub(
        main_driver: webdriver.Chrome
    ) -> pd.DataFrame:
        """
        Fonction interne permettant de recolter les informations des combattants de l'UFC

        Args:
            main_driver (webdriver): Objet webdriver de la page principale
            essais (int, optional): Nombre de tentatives. None par default.

        Returns:
            pd.Dataframe: Dataframe contenant les informations des combattants
        """
        try:
            temp_liste = _recolte_pages_combattants(main_driver)

            options = Options()
            
            options.add_argument("--headless")

            sub_driver = webdriver.Chrome(options=options)

            for url in temp_liste:
                if url not in hrefs and not _deja_present(Data, url):
                    logger.info(f"Visite de la page {url}")
                    dictio = _visite_page_combattant(sub_driver, url)
                    if dictio is not None:
                        result.append(dictio)
                    hrefs.append(url)
        
            sub_driver.quit()

            _click_chargement_plus(main_driver)
            
            return _page_principal_sub(main_driver)

        except TimeoutException:
            logger.error(
                "TimeoutException : Le bouton de chargement n'a pas ete trouve. Fin de la pagination."
            )
        except WebDriverException as e:
            logger.error(f"Erreur WebDriver : {e}")
            hrefs.append(url)
            return _page_principal_sub(main_driver)

        except Exception as e:
            logger.error(f"Erreur inattendue : {e}")

        return pd.concat([Data, pd.DataFrame(result)], ignore_index=True)
    
    return _page_principal_sub(main_driver)


if __name__ == "__main__":

    main_driver = webdriver.Chrome()

    data = _page_principal_UFC(main_driver)

    data.to_json("data/combattant_ufc.json", orient="records")
