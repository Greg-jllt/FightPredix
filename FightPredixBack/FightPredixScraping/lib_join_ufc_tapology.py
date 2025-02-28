"""
Librairie pour joindre les données de l'UFC et de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import polars as pl
import logging

from FightPredixBack.FightPredixScraping.lib_nettoyage_tapology import (
    _main_nettoyage_tapology,
)
from FightPredixBack.FightPredixScraping.lib_scraping_tapology import (
    _main_scraping_tapology,
)


def _main_tapology():
    logging.info("Nettoyage des données de tapology")

    recuperer_ancien_scraping = True
    if recuperer_ancien_scraping:
        data_tapology = pl.read_json(
            "FightPredixBack/FightPredixScraping/temp_data/clean_tapology.json"
        )
    else:
        _main_scraping_tapology()
        _main_nettoyage_tapology()
        data_tapology = pl.read_json(
            "FightPredixBack/FightPredixScraping/temp_data/clean_tapology.json"
        )

    data_ufc = pl.read_json(
        "FightPredixBack/FightPredixScraping/temp_data/Data_ufc_fighters.json"
    )

    data_join = data_ufc.join(data_tapology, on="NAME", how="left").unique()

    return data_join
