# """Teste les fonctions de lib_characteristics_collection.py"""

# import pandas as pd
# import pytest
# from FightPredix.lib_caracteristic_collector import (
#     _infos_principal_combattant,
#     _combattant_actif,
#     _bio_combattant,
#     _tenant_titre,
#     _stats_combattant,
#     _stats_corps_combattant,
#     _pourcentage_touche_takedown,
#     _mesures_combattant,
# )
# from bs4 import BeautifulSoup
# from collections import defaultdict

# from .fixtures import webdriver, url, url_combattant, soup_combattant


# def test_infos_principal_combattant(soup_combattant):
#     """
#     Fonction qui teste la fonction _infos_principal_combattant
#     """

#     dictio = defaultdict()
#     fiche_combattant = soup_combattant.find_all("div", class_="c-hero__headline")
#     dictio["Name"] = (
#         soup_combattant.select_one("div.hero-profile > div.hero-profile__info")
#         .find("h1")
#         .text
#     )
#     assert dictio["Name"] == "Danny Abbadi"

#     _infos_principal_combattant(fiche_combattant, dictio)

#     assert dictio["Win"] == 2
#     assert dictio["Losses"] == 2
#     assert dictio["Draws"] == 0
#     assert dictio["Division"] == "Lightweight Division"
#     assert dictio["Genre"] == "Male"


# def test_combattant_actif(soup_combattant):
#     """
#     Fonction qui teste la fonction _combattant_actif
#     """

#     dictio = defaultdict()
#     _combattant_actif(soup_combattant, dictio)
#     assert dictio["Actif"]


# def test_bio_combattant(soup_combattant):
#     """
#     Fonction qui teste la fonction _bio_combattant
#     """

#     dictio = defaultdict()
#     info_combattant = soup_combattant.find_all("div", class_="c-bio__row")
#     required = [
#         "Nationalité",
#         "Lieu de naissance",
#         "Taille",
#         "Poids",
#         "Entrainé par",
#         "Date de naissance",
#     ]

#     _bio_combattant(info_combattant, dictio, required)

#     assert dictio["Âge"] == 39.0
#     assert dictio["La Taille"] == 71.0
#     assert dictio["Poids"] == 156.0


# def test_tenant_titre(soup_combattant):
#     """
#     Fonction qui teste la fonction _tenant_titre
#     """

#     dictio = defaultdict()
#     _tenant_titre(soup_combattant, dictio)
#     assert not dictio["Tenant Titre"]


# def test_stats_combattants(soup_combattant):
#     """
#     Fonction qui teste la fonction _stats_combattant
#     """

#     dictio = defaultdict()
#     _stats_combattant(soup_combattant, dictio)

#     assert dictio["Permanent"] is None
#     assert dictio["Clinch"] is None
#     assert dictio["Sol"] is None
#     assert dictio["KO/TKO"] is None
#     assert dictio["DEC"] is None
#     assert dictio["SUB"] is None


# def test_stats_corps_combattant(soup_combattant):
#     """
#     Fonction qui teste la fonction _stats_corps_combattant
#     """

#     dictio = defaultdict()
#     _stats_corps_combattant(soup_combattant, dictio)

#     assert dictio["sig_str_head"] is None
#     assert dictio["sig_str_body"] is None
#     assert dictio["sig_str_leg"] is None


# def test_pourcentage_touche_takedown(soup_combattant):
#     """
#     Fonction qui teste la fonction _pourcentage_touche_takedown
#     """

#     dictio = defaultdict()
#     _pourcentage_touche_takedown(soup_combattant, dictio)

#     assert dictio["Précision_saisissante"] is None
#     assert dictio["Précision_de_Takedown"] is None


# def test_mesures_combattant(soup_combattant):
#     """
#     Fonction qui teste la fonction _mesures_combattant
#     """

#     dictio = defaultdict()
#     _mesures_combattant(soup_combattant, dictio)

#     assert dictio["Sig. Str. A atterri"] is None
#     assert dictio["Sig. Frappes Encaissées"] is None
#     assert dictio["Takedown avg"] is None
#     assert dictio["Envoi avg"] is None
#     assert dictio["Sig. Str.défense"] is None
#     assert dictio["Défense de démolition"] is None
#     assert dictio["Knockdown Avg"] is None
#     assert dictio["Temps de combat moyen"] is None
