"""
Librairie pour joindre les données de l'UFC et de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import polars as pl
import subprocess
import logging


if __name__ == "__main__":
    logging.info("Nettoyage des données de tapology")
    subprocess.run(["python", "-m", "FightPredix.lib_clean_tapology"], shell=True)

    data_ufc = pl.read_csv("../../donnees_finales/Data_ufc_fighters.csv")
    data_tapology = pl.read_csv(
        "../../donnees_finales/actual_clean_combattant_tapology.csv"
    )

    data_join = data_ufc.join(data_tapology, on="NAME", how="left").unique()

    data_join.to_pandas().to_csv("../../donnees_finales/Data_jointes.csv", index=False)
