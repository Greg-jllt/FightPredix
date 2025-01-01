"""
Librairie de fonctions pour la recolte des combats

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from selenium.webdriver.common.by import By
from selenium import webdriver
from rich.console import Console

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


def _couleur_combattant(driver: webdriver.Chrome, winner : str) -> dict:
    """
    Fonction pour récupérer les couleurs des combattants en fonction du gagnant.
    """
    combattant_colors = driver.find_elements(By.CSS_SELECTOR, "i.b-fight-details__charts-name.b-fight-details__charts-name_pos_left.js-chart-name, i.b-fight-details__charts-name.b-fight-details__charts-name_pos_right.js-chart-name")
    temp_dict = {}
    for color in combattant_colors:
        couleur = color.get_attribute("data-color")
        if color.text == winner:
            temp_dict["winner_color"] = couleur
        else : 
            temp_dict["looser_color"] = couleur

    return temp_dict


def _get_combattant_data(frappe_types, elements_cbt_1, elements_cbt_2, color, temp_dict) -> dict:
    """
    Fonction pour récupérer les données d'un combattant en fonction de sa couleur.
    """
    selected_elements = elements_cbt_1 if color == "red" else elements_cbt_2
    return ({f"combattant_1_{frappe_type}": frappe.text for frappe_type, frappe in zip(frappe_types, selected_elements)} if color == temp_dict["winner_color"]
        else {f"combattant_2_{frappe_type}": frappe.text for frappe_type, frappe in zip(frappe_types, selected_elements)})



def _explore_events(driver: webdriver.Chrome, row_data_link : str, winner : str, frappe_types : list[str]) -> dict:
    """
    Fonction qui explore les events et recolte les données
    """

    driver.get(row_data_link)

    temp_dict = _couleur_combattant(driver, winner)

    driver.find_element(By.CSS_SELECTOR, "div.b-fight-details__charts-col")

    elements_cbt_1 = driver.find_elements(By.CSS_SELECTOR, 
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-red")
    
    elements_cbt_2 = driver.find_elements(By.CSS_SELECTOR,
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-blue")

    winner_data = _get_combattant_data(frappe_types, elements_cbt_1, elements_cbt_2, temp_dict["winner_color"], temp_dict)
    looser_data = _get_combattant_data(frappe_types, elements_cbt_1, elements_cbt_2, temp_dict["looser_color"], temp_dict)

    result = {**winner_data, **looser_data}

    logger.info(result)

    return result

    

def _acces_events(liste_events:list, driver : webdriver.Chrome) -> dict:
    """
    Fonction qui explore les events et recolte les combats, 50% sont des 0 et 50% des 1, la structure de la page place toujours le nom du combattant gagnant en premier l'algo place le gagnant en premier une fois sur deux 

    Args:
        liste_events (list): liste des events
        driver (webdriver): objet webdriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    sub_driver = webdriver.Chrome(options=options)
    frappe_types = ["frappe_tete", "frappe_corps", "frappe_jambe", "frappe_distance", "frappe_clinch", "frappe_sol"]
    results = [] 
    i=0

    for event in liste_events:

        logger.info(f"Event : {event}")

        driver.get(event)  
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.b-fight-details__table-row")[1:]

        for row in rows:
            row_data_link = row.get_attribute("data-link")

            for cbts , methodes in zip(row.find_elements(By.CSS_SELECTOR, "td.b-fight-details__table-col.l-page_align_left[style='width:100px']"),
                                        row.find_elements(By.CSS_SELECTOR, "td.b-fight-details__table-col.l-page_align_left:not([style='width:100%'])")[2::3]):
                
                methode_text = methodes.find_elements(By.TAG_NAME, "p")[0].text

                if methode_text in ["Overturned", "CNC"]:
                    break

                cbt = cbts.find_elements(By.TAG_NAME, "p")

                winner = cbt[0].text
                resultats = _explore_events(sub_driver, row_data_link, winner, frappe_types)
            
                combattant_1, combattant_2 = (cbt[0].text, cbt[1].text) if i % 2 == 0 else (cbt[1].text, cbt[0].text)

                logger.info(f"Combattant 1 : {combattant_1} Combattant 2 : {combattant_2}")

                resultat = 0 if i % 2 == 0 else 1

                combattant_1_frappe = {f"combattant_1_{metric}": resultats[f"combattant_1_{metric}"] if i % 2 == 0 else resultats[f"combattant_2_{metric}"] 
                                      for metric in frappe_types}

                combattant_2_frappe = {f"combattant_2_{metric}": resultats[f"combattant_2_{metric}"] if i % 2 == 0 else resultats[f"combattant_1_{metric}"] 
                                      for metric in frappe_types}
                

                results.append({
                    "combattant_1": combattant_1,
                    "combattant_2": combattant_2,
                    "resultat": resultat,
                    "methode": methode_text[2:5] if methode_text in ["U-DEC", "S-DEC", "M-DEC"] else methode_text,
                    **combattant_1_frappe,
                    **combattant_2_frappe
                })

                i += 1
            


def _main_combat_recolte(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    fonction principale de recolte des combats sur UFC stats 

    Args:
        driver (webdriver): objet webdriver
    """

    logger.info("Lancement de la recolte des combats")

    liste_events = _recolte_events(driver)

    res = _acces_events(liste_events, driver)

    return pd.DataFrame(res)


if __name__ == "__main__":

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    data = _main_combat_recolte(driver)

    # data.to_csv("FightPredixApp/Data/Data_ufc_combats.csv", index=False)

    driver.quit()
