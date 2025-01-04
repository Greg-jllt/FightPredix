"""
Fichier de test pour la librairie de recolte des combats
"""

import os
import sys
from scraping.lib_combats import (
    _explore_events,
)

from .fixtures import driver_ufc_stats_combats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_main_combat_recolte():
    res = [
        {
            "combattant_1": "Alexandre Pantoja",
            "combattant_2": "Kai Asakura",
            "resultat": 0,
            "methode": "SUB",
        },
        {
            "combattant_1": "Ian Machado Garry",
            "combattant_2": "Shavkat Rakhmonov",
            "resultat": 1,
            "methode": "DEC",
        },
        {
            "combattant_1": "Ciryl Gane",
            "combattant_2": "Alexander Volkov",
            "resultat": 0,
            "methode": "DEC",
        },
        {
            "combattant_1": "Kron Gracie",
            "combattant_2": "Bryce Mitchell",
            "resultat": 1,
            "methode": "KO/TKO",
        },
        {
            "combattant_1": "Dooho Choi",
            "combattant_2": "Nate Landwehr",
            "resultat": 0,
            "methode": "KO/TKO",
        },
        {
            "combattant_1": "Anthony Smith",
            "combattant_2": "Dominick Reyes",
            "resultat": 1,
            "methode": "KO/TKO",
        },
        {
            "combattant_1": "Vicente Luque",
            "combattant_2": "Themba Gorimbo",
            "resultat": 0,
            "methode": "SUB",
        },
        {
            "combattant_1": "Aljamain Sterling",
            "combattant_2": "Movsar Evloev",
            "resultat": 1,
            "methode": "DEC",
        },
        {
            "combattant_1": "Bryan Battle",
            "combattant_2": "Randy Brown",
            "resultat": 0,
            "methode": "DEC",
        },
        {
            "combattant_1": "Chris Weidman",
            "combattant_2": "Eryk Anders",
            "resultat": 1,
            "methode": "KO/TKO",
        },
        {
            "combattant_1": "Joshua Van",
            "combattant_2": "Cody Durden",
            "resultat": 0,
            "methode": "DEC",
        },
        {
            "combattant_1": "Max Griffin",
            "combattant_2": "Michael Chiesa",
            "resultat": 1,
            "methode": "SUB",
        },
        {
            "combattant_1": "Chase Hooper",
            "combattant_2": "Clay Guida",
            "resultat": 0,
            "methode": "SUB",
        },
        {
            "combattant_1": "Lukasz Brzeski",
            "combattant_2": "Kennedy Nzechukwu",
            "resultat": 1,
            "methode": "KO/TKO",
        },
    ]
    driver, _ = driver_ufc_stats_combats()
    assert _explore_events(liste_events=["http://www.ufcstats.com/event-details/ad23903ef3af7406"], driver=driver) == res
