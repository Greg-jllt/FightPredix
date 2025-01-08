"""
Librairie de fonctions permettant de calculer les statistiques cumulatives des combattants

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from datetime import datetime
from math import nan
import pandas as pd
import json
from .outils import configure_logger

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_stats")


def _sub_format_date(date, format_actuel, format_voulu):
    date_obj = datetime.strptime(date, format_actuel)
    formatted_date = date_obj.strftime(format_voulu)
    return formatted_date


def _format_date(data: pd.DataFrame):
    new_dates = []
    for date in data["date"]:
        new_dates.append(_sub_format_date(date, "%B %d, %Y", "%Y-%m-%d"))

    data["date"] = new_dates


def _calcul_stat_cumul(
    data: pd.DataFrame,
    data_combattant: pd.DataFrame,
    nom: str,
    dico_var: dict[str, tuple[str, str]],
) -> pd.DataFrame:
    """
    Fonction qui permet de calculer les statistiques cumulatives d'un combattant
    en fonction des combats qu'il a effectué.
    """
    dico_last_combat = dict()
    for stat in dico_var.keys():
        stat_sans_combattant = stat.split("combattant")[1]

        somme_cumulative = 0
        denominateur = 0

        moyennes_cumulatives: list[float] = []
        stat_t_1: list[float] = []
        liste_num_du_combattant = []

        for num_row in range(len(data_combattant)):
            if data_combattant.iloc[num_row]["combattant_1"] == nom:
                pourcentage = data_combattant.iloc[num_row][f"{dico_var[stat][0]}"]
                liste_num_du_combattant.append(1)
            else:
                pourcentage = data_combattant.iloc[num_row][f"{dico_var[stat][1]}"]
                liste_num_du_combattant.append(2)

            if pd.isna(pourcentage):
                denominateur = denominateur
                somme_cumulative = somme_cumulative
                stat_t_1.append(nan)
            else:
                denominateur = denominateur + 1
                somme_cumulative += pourcentage
                stat_t_1.append(pourcentage)

            if denominateur == 0:
                moyennes_cumulatives.append(nan)
            else:
                moyenne_cumulative = round(somme_cumulative / denominateur, 2)
                moyennes_cumulatives.append(moyenne_cumulative)

        for index, num_combattant, moyenne, stat_t in zip(
            data_combattant.index[1:],
            liste_num_du_combattant[1:],
            moyennes_cumulatives[:-1],
            stat_t_1[:-1],
        ):
            data.loc[
                index, f"combattant_{num_combattant}{stat_sans_combattant}_moyenne"
            ] = moyenne
            data.loc[
                index, f"combattant_{num_combattant}{stat_sans_combattant}_t_1"
            ] = stat_t

        dico_last_combat[f"{stat_sans_combattant}_moyenne"] = moyennes_cumulatives[-1]
        dico_last_combat[f"{stat_sans_combattant}_t_1"] = stat_t_1[-1]

    return data, dico_last_combat


def _rattraper_combattant_nom_identique(data: pd.DataFrame, nom: str) -> pd.DataFrame:
    """
    Fonction qui permet de rattraper les combattants qui ont le même nom.
    """
    nicknames = (
        data[data["combattant_1"] == nom]["nickname_1"].unique().tolist()
        + data[data["combattant_2"] == nom]["nickname_2"].unique().tolist()
    )
    return nicknames


def _assignement_stat_combattant(
    data: pd.DataFrame, dico_var: dict[str, tuple[str, str]]
) -> tuple[pd.DataFrame, dict, dict]:
    """
    Fonction qui permet d'assigner les statistiques des combattants dans le dataframe.
    """
    _format_date(data)

    new_columns: dict[str, float] = dict()
    dico_last_combat = dict()
    dico_last_combat_nom_identique = dict()
    for stat in dico_var.keys():
        stat_sans_combattant = stat.split("combattant_")[1]
        new_columns[f"combattant_1{stat_sans_combattant}_moyenne"] = nan
        new_columns[f"combattant_2{stat_sans_combattant}_moyenne"] = nan
        new_columns[f"combattant_1{stat_sans_combattant}_t_1"] = nan
        new_columns[f"combattant_2{stat_sans_combattant}_t_1"] = nan

    new_columns_df = pd.DataFrame(new_columns, index=data.index)
    data = pd.concat([data, new_columns_df], axis=1)

    combattants = set(data["combattant_1"].tolist() + data["combattant_2"].tolist())
    liste_combattants = list(combattants)
    nom_identiques = ["Dong Hyun Kim", "Bruno Silva", "Joey Gomez"]
    for nom in liste_combattants:
        if nom not in nom_identiques:
            logger.info(f"Calcul des statistiques cumulatives pour le combattant {nom}")
            data_combattant = pd.concat(
                [data[data["combattant_1"] == nom], data[data["combattant_2"] == nom]]
            ).sort_index(ascending=False)

            data, dico = _calcul_stat_cumul(data, data_combattant, nom, dico_var)
            dico_last_combat[f"{nom}"] = dico
        else:
            logger.info(f"Rattrapage du combattant {nom}")
            nicknames = _rattraper_combattant_nom_identique(data, nom)
            for nickname in nicknames:
                data_combattant = pd.concat(
                    [
                        data[
                            (data["nickname_1"] == nickname)
                            & (data["combattant_1"] == nom)
                        ],
                        data[
                            (data["nickname_2"] == nickname)
                            & (data["combattant_2"] == nom)
                        ],
                    ]
                ).sort_index(ascending=False)

                data, dico = _calcul_stat_cumul(data, data_combattant, nom, dico_var)
                dico_last_combat_nom_identique[f"{nickname}"] = dico

    return data, dico_last_combat, dico_last_combat_nom_identique


if __name__ == "__main__":
    with open("dico_var.json", "r") as file:
        dico_var = json.load(file)

    data = pd.read_csv("data/Data_ufc_combat_complet_actuel_clean.csv")

    data, dico_last_stat, dico_last_stat_nom_identique = _assignement_stat_combattant(
        data, dico_var
    )

    data.to_csv("data/Data_ufc_combat_complet_actuel_clean.csv", index=False)
    with open("data/dico_last_stat.json", "w") as file:
        json.dump(dico_last_stat, file)
