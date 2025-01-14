"""
Librairie pour joindre les données de l'UFC et de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import polars as pl
import subprocess
import logging

from lib_nettoyage_tapology import _main_nettoyage_tapology
from lib_scraping_tapology import _main_scraping_tapology


def _main_tapology():
    logging.info("Nettoyage des données de tapology")
    
    _main_scraping_tapology()
    _main_nettoyage_tapology()

    data_ufc = pl.read_json("Data/Data_ufc_fighters.json")
    data_tapology = pl.read_json("Data/clean_tapology.json")

    data_join = data_ufc.join(data_tapology, on="NAME", how="left").unique()

    return data_join


if __name__ == "__main__":

    data_join = _main_tapology()

    data_join.to_pandas().to_json("Data/Data_jointes_ufc_tapology.json", orient="columns", index=False)
