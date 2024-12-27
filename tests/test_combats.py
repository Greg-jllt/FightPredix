"""
Fichier de test pour la librairie de recolte des combats
"""

import pytest

from FightPredix.lib_combats import (
    _explore_events,
)

from .fixtures import driver_ufc_stats_combats

def test_main_combat_recolte():
    res = [
 {'combattant_1': 'Alexandre Pantoja',
  'combattant_2': 'Kai Asakura',
  'resultat': 0},
 {'combattant_1': 'Ian Machado Garry',
  'combattant_2': 'Shavkat Rakhmonov',
  'resultat': 1},
 {'combattant_1': 'Ciryl Gane',
  'combattant_2': 'Alexander Volkov',
  'resultat': 0},
 {'combattant_1': 'Kron Gracie',
  'combattant_2': 'Bryce Mitchell',
  'resultat': 1},
 {'combattant_1': 'Dooho Choi',
  'combattant_2': 'Nate Landwehr',
  'resultat': 0},
 {'combattant_1': 'Anthony Smith',
  'combattant_2': 'Dominick Reyes',
  'resultat': 1},
 {'combattant_1': 'Vicente Luque',
  'combattant_2': 'Themba Gorimbo',
  'resultat': 0},
 {'combattant_1': 'Aljamain Sterling',
  'combattant_2': 'Movsar Evloev',
  'resultat': 1},
 {'combattant_1': 'Bryan Battle',
  'combattant_2': 'Randy Brown',
  'resultat': 0},
 {'combattant_1': 'Chris Weidman',
  'combattant_2': 'Eryk Anders',
  'resultat': 1},
 {'combattant_1': 'Joshua Van', 
  'combattant_2': 'Cody Durden', 
  'resultat': 0},
 {'combattant_1': 'Max Griffin',
  'combattant_2': 'Michael Chiesa',
  'resultat': 1},
 {'combattant_1': 'Chase Hooper', 
  'combattant_2': 'Clay Guida', 
  'resultat': 0},
 {'combattant_1': 'Lukasz Brzeski',
  'combattant_2': 'Kennedy Nzechukwu',
  'resultat': 1}
  ]
    driver, liste_events = driver_ufc_stats_combats()
    assert _explore_events(liste_events=liste_events, driver=driver) == res
