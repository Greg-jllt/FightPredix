"""
Module de test pour la librairie lib_combats.py
"""

import time
from selenium.webdriver.common.by import By
from FightPredixBack.FightPredixScraping.scraping.lib_combats import (
    _recolte_events,
    _couleur_combattant,
    _recolte_stat_combat,
    _get_combattant_data,
    _recup_donnes_total,
    _sub_fonction_listes,
)
import polars as pl
from bs4 import BeautifulSoup
from selenium import webdriver

from .fixtures import driver_ufc_stats_combats  # noqa F401


def test_recolte_events(driver_ufc_stats_combats):  # noqa F811
    """
    Test de la fonction recolte_events
    """

    liste_events = _recolte_events(driver_ufc_stats_combats)
    assert "http://www.ufcstats.com/event-details/221b2a3070c7ce3e" in liste_events
    assert "http://www.ufcstats.com/event-details/bbb15f301e4a490a" in liste_events
    assert "http://www.ufcstats.com/event-details/02fc8f50f56eb307" in liste_events


def test_couleur_combattant(driver_ufc_stats_combats):  # noqa F811
    """
    Test de la fonction couleur_combattant
    """

    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )
    color_dict = _couleur_combattant(driver_ufc_stats_combats, "Alexandre Pantoja")
    assert "red" in color_dict["winner_color"]
    assert "blue" in color_dict["looser_color"]


def test_get_combattant_data(driver_ufc_stats_combats):  # noqa F811
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


def test_recup_donnes_totales():
    """
    Test de la fonction recup_donnes_totales
    """
    time.sleep(5)
    driver = webdriver.Chrome()
    driver.get("http://www.ufcstats.com/fight-details/e761c5009c09b295")

    soup = BeautifulSoup(driver.page_source, "html.parser")

    assert isinstance(_recup_donnes_total(soup), pl.DataFrame)
    assert _recup_donnes_total(soup).shape == (2, 10)


def test_recolte_stat_combat(driver_ufc_stats_combats):  # noqa F811
    """
    Test de la fonction recolte_stat_combat
    """

    driver_ufc_stats_combats.get(
        "http://www.ufcstats.com/fight-details/e761c5009c09b295"
    )
    res = _recolte_stat_combat(
        lien_combat="http://www.ufcstats.com/fight-details/e761c5009c09b295",
        driver=driver_ufc_stats_combats,
        combattant_1="Alexandre Pantoja",
    )
    assert res.shape == (1, 44)
    assert res.columns.tolist() == [
        "nom_combat",
        "classe_combat",
        "Round",
        "Time",
        "Time format",
        "Referee",
        "combattant_1_Fightertotal",
        "combattant_1_KDtotal",
        "combattant_1_Sig. str.total",
        "combattant_1_Sig. str. %total",
        "combattant_1_Total str.total",
        "combattant_1_Tdtotal",
        "combattant_1_Td %total",
        "combattant_1_Sub. atttotal",
        "combattant_1_Rev.total",
        "combattant_1_Ctrltotal",
        "combattant_1_Fightersig_str_total",
        "combattant_1_Sig. strsig_str_total",
        "combattant_1_Sig. str. %sig_str_total",
        "combattant_1_Headsig_str_total",
        "combattant_1_Bodysig_str_total",
        "combattant_1_Legsig_str_total",
        "combattant_1_Distancesig_str_total",
        "combattant_1_Clinchsig_str_total",
        "combattant_1_Groundsig_str_total",
        "combattant_2_Fightertotal",
        "combattant_2_KDtotal",
        "combattant_2_Sig. str.total",
        "combattant_2_Sig. str. %total",
        "combattant_2_Total str.total",
        "combattant_2_Tdtotal",
        "combattant_2_Td %total",
        "combattant_2_Sub. atttotal",
        "combattant_2_Rev.total",
        "combattant_2_Ctrltotal",
        "combattant_2_Fightersig_str_total",
        "combattant_2_Sig. strsig_str_total",
        "combattant_2_Sig. str. %sig_str_total",
        "combattant_2_Headsig_str_total",
        "combattant_2_Bodysig_str_total",
        "combattant_2_Legsig_str_total",
        "combattant_2_Distancesig_str_total",
        "combattant_2_Clinchsig_str_total",
        "combattant_2_Groundsig_str_total",
    ]
