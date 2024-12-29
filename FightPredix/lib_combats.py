"""
Librairie de fonctions pour la recolte des combats
"""

from selenium.webdriver.common.by import By
from selenium import webdriver
from rapidfuzz import fuzz

import pandas as pd
from datetime import datetime

from .outils import configure_logger


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_combats_stats")


def _recolte_events(driver) -> list:
    """
    focntion de recolte des événements sportif depuis 2014
    """
    driver.get("http://www.ufcstats.com/statistics/events/completed?page=all")
    return [
            event.find_element(By.CSS_SELECTOR, "a").get_attribute("href") 
            for event in driver.find_elements(By.CSS_SELECTOR, ".b-statistics__table-content")[1:]
            if int(event.find_element(By.CSS_SELECTOR, "span.b-statistics__date").text.split(",")[-1].strip()) >= 2014
        ]


def _explore_events(liste_events:list, driver : webdriver.Chrome) -> list:
    """
    Fonction qui explore les events et recolte les combats, 50% sont des 0 et 50% des 1, la structure de la page place toujours le nom du combattant gagnant en premier l'algo place le gagnant en premier une fois sur deux 

    Args:
        liste_events (list): liste des events
        driver (webdriver): objet webdriver
        res (list): liste vide
    """
    return [
        {
            "combattant_1": cbt[0].text if i%2==0 else cbt[1].text,
            "combattant_2": cbt[1].text if i%2==0 else cbt[0].text,
            "resultat": 0 if i%2==0 else 1,
            "methode" : methode_text[2:5] if methode_text in ["U-DEC", "S-DEC", "M-DEC"] else methode_text
        }
        for event in liste_events
        if (logger.info(f"Event: {event}"), True)[1]
        for _ in [driver.get(event)]
        for (i, cbts) , methodes in zip(enumerate(driver.find_elements(By.CSS_SELECTOR, "td.b-fight-details__table-col.l-page_align_left[style='width:100px']")), driver.find_elements(By.CSS_SELECTOR, "td.b-fight-details__table-col.l-page_align_left:not([style='width:100%'])")[2::3])
        if(
            (methode_text := methodes.find_elements(By.TAG_NAME, "p")[0].text) and 
            (cbt := cbts.find_elements(By.TAG_NAME, "p"))
        )
        if (
            logger.info(f"Paire de combattants: {cbt[0].text} vs {cbt[1].text}"),
            True
        )[1]
        if (
            logger.info(f"Methode : {methode_text}"),
            True
        )[1]
    ]


def _main_combat_recolte(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    fonction principale de recolte des combats sur UFC stats 

    Args:
        driver (webdriver): objet webdriver
    """

    liste_events = _recolte_events(driver)

    res = _explore_events(liste_events, driver)

    return pd.DataFrame(res)


if __name__ == "__main__":

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    data = _main_combat_recolte(driver)

    data.to_csv("FightPredixApp/Data/Data_ufc_combats.csv", index=False)

    driver.quit()
