"""
Librairie pour joindre les données de l'UFC et de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import polars as pl
import subprocess
import logging


def _main_tapology():
    logging.info("Nettoyage des données de tapology")

    scrapper_tapology = False
    if scrapper_tapology:
        subprocess.run(
            ["python", "-m", "FightPredix_scraping.scraping.lib_scraping_tapology"],
            shell=True,
        )
    else:
        pass
    subprocess.run(
        ["python", "-m", "FightPredix_scraping.scraping.lib_clean_tapology"], shell=True
    )

    data_ufc = pl.read_csv("Data/Data_ufc_fighters.csv")
    data_tapology = pl.read_csv("Data/clean_tapology.csv")

    data_join = data_ufc.join(data_tapology, on="NAME", how="left").unique()

    return data_join


if __name__ == "__main__":

    data_join = _main_tapology()

    data_join.to_pandas().to_csv("data/Data_jointes_ufc_tapology.csv", index=False)
