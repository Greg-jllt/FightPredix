"""
Librairie de fonctions pour la recolte des combats

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from bs4 import BeautifulSoup
import polars as pl
import pandas as pd
from datetime import datetime
from outils import configure_logger
import re
from typing import Any


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_combats_stats")


def _recolte_events(driver) -> list[str]:
    """
    focntion de recolte des événements sportif
    """
    driver.get("http://www.ufcstats.com/statistics/events/completed?page=all")
    return [
        event.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
        for event in driver.find_elements(
            By.CSS_SELECTOR, ".b-statistics__table-content"
        )[1:]
    ]


def _couleur_combattant(driver: webdriver.Chrome, winner: str) -> dict[str, str]:
    """
    Fonction pour récupérer les couleurs des combattants en fonction du gagnant.
    """
    combattant_colors = driver.find_elements(
        By.CSS_SELECTOR,
        "i.b-fight-details__charts-name.b-fight-details__charts-name_pos_left.js-chart-name, i.b-fight-details__charts-name.b-fight-details__charts-name_pos_right.js-chart-name",
    )
    temp_dict = {}
    for color in combattant_colors:
        couleur = color.get_attribute("data-color")
        if color.text == winner:
            temp_dict["winner_color"] = couleur
        else:
            temp_dict["looser_color"] = couleur

    return temp_dict


def _get_combattant_data(
    frappe_types: list[str],
    elements_cbt_1: WebElement,
    elements_cbt_2: WebElement,
    color: str,
    temp_dict: dict[str, str],
) -> dict[str, str]:
    """
    Fonction pour récupérer les données d'un combattant en fonction de sa couleur.
    """
    selected_elements = elements_cbt_1 if color == "red" else elements_cbt_2
    return (
        {
            f"combattant_1_{frappe_type}": frappe.text
            for frappe_type, frappe in zip(frappe_types, selected_elements)
        }
        if color == temp_dict["winner_color"]
        else {
            f"combattant_2_{frappe_type}": frappe.text
            for frappe_type, frappe in zip(frappe_types, selected_elements)
        }
    )


def _explore_events(
    driver: webdriver.Chrome, row_data_link: str, winner: str, frappe_types: list[str]
) -> dict:
    """
    Fonction qui explore les events et recolte les donnÃ©es
    """

    driver.get(row_data_link)
    temp_dict = _couleur_combattant(driver, winner)

    driver.find_element(By.CSS_SELECTOR, "div.b-fight-details__charts-col")

    elements_cbt_1 = driver.find_elements(
        By.CSS_SELECTOR,
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-red",
    )

    elements_cbt_2 = driver.find_elements(
        By.CSS_SELECTOR,
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-blue",
    )

    winner_data = _get_combattant_data(
        frappe_types,
        elements_cbt_1,
        elements_cbt_2,
        temp_dict["winner_color"],
        temp_dict,
    )
    looser_data = _get_combattant_data(
        frappe_types,
        elements_cbt_1,
        elements_cbt_2,
        temp_dict["looser_color"],
        temp_dict,
    )

    result = {**winner_data, **looser_data}

    logger.info(result)

    return result


def _sub_access_events(
    row: WebElement,
    results: list[pd.DataFrame],
    i: int,
    driver: webdriver.Chrome,
    sub_driver: webdriver.Chrome,
    frappe_types: list[str],
    row_data_link: str,
) -> tuple[list[pd.DataFrame], int]:
    """
    Fonction qui explore les events et recolte les combats, 50% sont des 0 et 50% des 1, la structure de la page place toujours le nom du combattant gagnant en premier l'algo place le gagnant en premier une fois sur deux
    """

    for cbts, methodes in zip(
        row.find_elements(
            By.CSS_SELECTOR,
            "td.b-fight-details__table-col.l-page_align_left[style='width:100px']",
        ),
        row.find_elements(
            By.CSS_SELECTOR,
            "td.b-fight-details__table-col.l-page_align_left:not([style='width:100%'])",
        )[2::3],
    ):
        methode_text = methodes.find_elements(By.TAG_NAME, "p")[0].text
        cbt = cbts.find_elements(By.TAG_NAME, "p")

        if methode_text in ["CNC", "Overturned"]:
            break

        winner = cbt[0].text
        resultats = _explore_events(sub_driver, row_data_link, winner, frappe_types)

        combattant_1, combattant_2 = (
            (cbt[0].text, cbt[1].text) if i % 2 == 0 else (cbt[1].text, cbt[0].text)
        )

        logger.info(f"Combattant 1 : {combattant_1} Combattant 2 : {combattant_2}")

        resultat = 0 if i % 2 == 0 else 1

        combattant_1_frappe = {
            f"combattant_1_{metric}": (
                resultats[f"combattant_1_{metric}"]
                if i % 2 == 0
                else resultats[f"combattant_2_{metric}"]
            )
            for metric in frappe_types
        }

        combattant_2_frappe = {
            f"combattant_2_{metric}": (
                resultats[f"combattant_2_{metric}"]
                if i % 2 == 0
                else resultats[f"combattant_1_{metric}"]
            )
            for metric in frappe_types
        }

        temp_dict = {
            "date": driver.find_element(
                By.XPATH, "/html/body/section/div/div/div[1]/ul/li[1]"
            )
            .text.split(":")[-1]
            .strip(),
            "lien_combat": row_data_link,
            "combattant_1": combattant_1,
            "combattant_2": combattant_2,
            "resultat": resultat,
            "methode": (
                methode_text[2:5]
                if methode_text in ["U-DEC", "S-DEC", "M-DEC"]
                else methode_text
            ),
            **combattant_1_frappe,
            **combattant_2_frappe,
        }

        temp_data = pd.DataFrame(temp_dict, index=[0])
        stats = _recolte_stat_combat(row_data_link, sub_driver, combattant_1)

        results.append(pd.concat([temp_data, stats], axis=1))
        i += 1
    return results, i


def _acces_events(liste_events: list, driver: webdriver.Chrome) -> pd.DataFrame:
    """
    Fonction qui explore les events et recolte les combats, 50% sont des 0 et 50% des 1, la structure de la page place toujours le nom du combattant gagnant en premier l'algo place le gagnant en premier une fois sur deux

    Args:
        liste_events (list): liste des events
        driver (webdriver): objet webdriver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    sub_driver = webdriver.Chrome(options=options)
    frappe_types = [
        "frappe_tete",
        "frappe_corps",
        "frappe_jambe",
        "frappe_distance",
        "frappe_clinch",
        "frappe_sol",
    ]

    results: list[pd.DataFrame] = []
    i = 0
    for event in liste_events:
        try:
            logger.info(f"Event : {event}")

            driver.get(event)
            rows = driver.find_elements(
                By.CSS_SELECTOR, "tr.b-fight-details__table-row"
            )[1:]

            for row in rows:
                row_data_link = row.get_attribute("data-link")

                results, i = _sub_access_events(
                    row, results, i, driver, sub_driver, frappe_types, row_data_link
                )

        except (Exception, KeyboardInterrupt) as e:
            logger.error(f"Erreur : {e}")
            pass
    return pd.concat(results)


def _sub_fonction_listes(data: pl.DataFrame) -> tuple[list[Any], list[Any]]:
    """
    Fonction pour récupérer les listes de valeurs
    """

    list_values1, list_values2 = zip(
        *[
            (value1.strip(), value2.strip())
            for cellule in data.get_columns()
            for value1, value2 in [cellule[0].split("\n", maxsplit=1)]
        ]
    )
    list_values1_to_return, list_values2_to_return = (
        list(list_values1),
        list(list_values2),
    )

    return list_values1_to_return, list_values2_to_return


def _recup_donnes_total(soup: BeautifulSoup) -> pl.DataFrame:
    """
    Fonction de recolte des statistiques totales des combats
    """
    table = soup.select_one("table")

    dictio_total = {
        col.text.strip() + "total": row.text.strip()
        for col, row in zip(
            table.find_all("th", class_="b-fight-details__table-col"),
            table.find_all("td", class_="b-fight-details__table-col"),
        )
    }

    merge_dict = {**dictio_total}

    data = pl.DataFrame(merge_dict)

    list_values1, list_values2 = _sub_fonction_listes(data)

    Totals = pl.DataFrame()
    for col, value1, value2 in zip(data.get_columns(), list_values1, list_values2):
        Totals = Totals.with_columns(pl.Series(str(col.name), [value1, value2]))

    return Totals


def _recup_donnes_sig_str(soup: BeautifulSoup) -> dict:
    """
    Fonction de recolte des statistiques des combats
    """

    table = soup.select("table")
    table = table[3]

    dictio_sig_str_total = {}
    for index, (col, row) in enumerate(
        zip(
            table.find_all("th", class_="b-fight-details__table-col"),
            table.find_all("td", class_="b-fight-details__table-col"),
        )
    ):
        dictio_sig_str_total[col.text.strip() + "sig_str_total"] = row.text.strip()
        if index == 8:
            break

    merge_dict_sig_str = {**dictio_sig_str_total}

    data = pl.DataFrame(merge_dict_sig_str)

    list_values1, list_values2 = _sub_fonction_listes(data)

    Totals_sig_str = pl.DataFrame()
    for col, value1, value2 in zip(data.get_columns(), list_values1, list_values2):
        Totals_sig_str = Totals_sig_str.with_columns(
            pl.Series(str(col.name), [value1, value2])
        )

    return Totals_sig_str


def _recolte_stat_combat(
    lien_combat: str, driver: webdriver.Chrome, combattant_1: str
) -> pd.DataFrame:
    """
    Fonction de recolte des statistiques des combats
    """

    driver.implicitly_wait(50)
    driver.get(lien_combat)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Récupération des données de base (nom_combat, nom_combattant_1, nom_combattant_2, classe_combat)
    nom_combat = driver.find_element(By.XPATH, "/html/body/section/div/h2/a").text
    classe_combat = driver.find_element(
        By.XPATH, "/html/body/section/div/div/div[2]/div[1]/i"
    ).text
    dictio = {}
    dictio["nom_combat"] = nom_combat
    dictio["classe_combat"] = classe_combat
    for element in soup.find_all("i", class_="b-fight-details__text-item"):
        try:
            element1, element2 = element.text.split(":", maxsplit=1)
            dictio[element1.strip()] = element2.strip()
        except ValueError:
            pass

    general_data = pl.DataFrame(dictio)

    Totals = _recup_donnes_total(driver, soup)

    Totals_sig_str = _recup_donnes_sig_str(driver, soup)

    if combattant_1 == Totals["Fightertotal"][0]:
        ligne1_total = Totals[0].rename(
            {col: f"combattant_1_{col}" for col in Totals[0].columns}
        )
        ligne2_total = Totals[1].rename(
            {col: f"combattant_2_{col}" for col in Totals[1].columns}
        )
        ligne1_sig_str = Totals_sig_str[0].rename(
            {col: f"combattant_1_{col}" for col in Totals_sig_str[0].columns}
        )
        ligne2_sig_str = Totals_sig_str[1].rename(
            {col: f"combattant_2_{col}" for col in Totals_sig_str[1].columns}
        )
    else:
        ligne2_total = Totals[0].rename(
            {col: f"combattant_2_{col}" for col in Totals[1].columns}
        )
        ligne1_total = Totals[1].rename(
            {col: f"combattant_1_{col}" for col in Totals[0].columns}
        )
        ligne2_sig_str = Totals_sig_str[0].rename(
            {col: f"combattant_2_{col}" for col in Totals_sig_str[1].columns}
        )
        ligne1_sig_str = Totals_sig_str[1].rename(
            {col: f"combattant_1_{col}" for col in Totals_sig_str[0].columns}
        )

    combat = pl.concat(
        [general_data, ligne1_total, ligne1_sig_str, ligne2_total, ligne2_sig_str],
        how="horizontal",
    ).to_pandas()

    return combat


def _main_combat_recolte(driver: webdriver.Chrome) -> pd.DataFrame:
    """
    fonction principale de recolte des combats sur UFC stats

    Args:
        driver (webdriver): objet webdriver
    """

    logger.info("Lancement de la recolte des combats")

    liste_events = _recolte_events(driver)

    res = _acces_events(liste_events, driver)

    return res


if __name__ == "__main__":
    options = webdriver.ChromeOptions()

    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

    data = _main_combat_recolte(driver)

    data.to_json("Data/Data_ufc_stats_combats.json", index=False)

    driver.quit()
