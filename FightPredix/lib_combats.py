"""
Librairie de fonctions pour la recolte des combats
"""

from selenium.webdriver.common.by import By
from selenium import webdriver

import pandas as pd



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
            "combattant_1": cbt.find_elements(By.TAG_NAME, "p")[0].text if i%2==0 else cbt.find_elements(By.TAG_NAME, "p")[1].text,
            "combattant_2": cbt.find_elements(By.TAG_NAME, "p")[1].text if i%2==0 else cbt.find_elements(By.TAG_NAME, "p")[0].text,
            "resultat": 0 if i%2==0 else 1
        }
        for event in liste_events
        for _ in [driver.get(event)]
        for i, cbt in enumerate(driver.find_elements(By.CSS_SELECTOR, "td.b-fight-details__table-col.l-page_align_left[style='width:100px']"))
    ]


def main_combat_recolte(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    fonction principale de recolte des combats sur UFC stats 

    Args:
        driver (webdriver): objet webdriver
    """

    liste_events = _recolte_events(driver)

    res = _explore_events(liste_events, driver)

    return pd.DataFrame(res)