"""
Fichier de test pour la librairie de recolte des combats
"""

import os
import sys
from selenium.webdriver.common.by import By
from scraping.lib_combats import (
    _recolte_events,
    _couleur_combattant,
    _explore_events,
    _get_combattant_data,
    _main_combat_recolte,
    _recolte_stat_combat,
    _recup_donnes_sig_str,
    _recup_donnes_total,
    _sub_fonction_elements,
    _sub_fonction_listes,
    clean_column_nom,
)
import polars as pl
from bs4 import BeautifulSoup

from .fixtures import driver_ufc_stats_combats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_recolte_events(driver_ufc_stats_combats):
    """
    Test de la fonction recolte_events
    """

    liste_events = _recolte_events(driver_ufc_stats_combats)
    assert "http://www.ufcstats.com/event-details/221b2a3070c7ce3e" in liste_events
    assert "http://www.ufcstats.com/event-details/bbb15f301e4a490a" in liste_events
    assert "http://www.ufcstats.com/event-details/02fc8f50f56eb307" in liste_events


def test_couleur_combattant(driver_ufc_stats_combats):
    """
    Test de la fonction couleur_combattant
    """

    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )
    color_dict = _couleur_combattant(driver_ufc_stats_combats, "Alexandre Pantoja")
    assert "red" in color_dict["winner_color"]
    assert "blue" in color_dict["looser_color"]


def test_get_combattant_data(driver_ufc_stats_combats):
    """
    Test de la fonction get_combattant_data
    """

    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )
    elements_cbt_1 = driver_ufc_stats_combats.find_elements(
        By.CSS_SELECTOR,
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-red, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-red",
    )

    elements_cbt_2 = driver_ufc_stats_combats.find_elements(
        By.CSS_SELECTOR,
        "i.b-fight-details__charts-num.b-fight-details__charts-num_style_blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_dark-blue, i.b-fight-details__charts-num.b-fight-details__charts-num_style_light-blue",
    )
    res = _get_combattant_data(
        frappe_types=[
            "frappe_tete",
            "frappe_corps",
            "frappe_jambe",
            "frappe_distance",
            "frappe_clinch",
            "frappe_sol",
        ],
        elements_cbt_1=elements_cbt_1,
        elements_cbt_2=elements_cbt_2,
        color="red",
        temp_dict=dict(
            winner_color="red",
            looser_color="blue",
        ),
    )
    assert res == {
        "combattant_1_frappe_tete": "46%",
        "combattant_1_frappe_corps": "15%",
        "combattant_1_frappe_jambe": "37%",
        "combattant_1_frappe_distance": "93%",
        "combattant_1_frappe_clinch": "6%",
        "combattant_1_frappe_sol": "0%",
    }


def test_explore_events(driver_ufc_stats_combats):
    """
    Test de la fonction explore_events
    """

    result = _explore_events(
        driver=driver_ufc_stats_combats,
        row_data_link="http://www.ufcstats.com/fight-details/e761c5009c09b295",
        winner="Alexandre Pantoja",
        frappe_types=[
            "frappe_tete",
            "frappe_corps",
            "frappe_jambe",
            "frappe_distance",
            "frappe_clinch",
            "frappe_sol",
        ],
    )
    assert result == {
        "combattant_1_frappe_tete": "46%",
        "combattant_1_frappe_corps": "15%",
        "combattant_1_frappe_jambe": "37%",
        "combattant_1_frappe_distance": "93%",
        "combattant_1_frappe_clinch": "6%",
        "combattant_1_frappe_sol": "0%",
        "combattant_2_frappe_tete": "58%",
        "combattant_2_frappe_corps": "29%",
        "combattant_2_frappe_jambe": "11%",
        "combattant_2_frappe_distance": "100%",
        "combattant_2_frappe_clinch": "0%",
        "combattant_2_frappe_sol": "0%",
    }


def test_sub_fonction_listes():
    """
    Test de la fonction sub_fonction_listes
    """
    data = pl.DataFrame(
        {
            "fighters": "Alexandre Pantoja\n Ian Machado Garry\n\n",
            "stat1": "46%\n\n58%\n",
        }
    )
    assert _sub_fonction_listes(data) == (
        ["Alexandre Pantoja", "46%"],
        ["Ian Machado Garry", "58%"],
    )


def test_sub_fonction_elements(driver_ufc_stats_combats):
    """
    Test de la fonction sub_fonction_elements
    """
    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )
    elements = driver_ufc_stats_combats.find_elements(
        By.XPATH, "/html/body/section/div/div/section[3]/table"
    )
    dico = dict()
    assert len(_sub_fonction_elements(elements, dico)) == 2


def test_recup_donnes_totales(driver_ufc_stats_combats):
    """
    Test de la fonction recup_donnes_totales
    """

    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )

    soup = BeautifulSoup(driver_ufc_stats_combats.page_source, "html.parser")

    assert isinstance(_recup_donnes_total(driver_ufc_stats_combats, soup), pl.DataFrame)
    assert _recup_donnes_total(driver_ufc_stats_combats, soup).shape == (2, 30)
