"""
Module de construction de variables initialement non présentes dans les variables scrapé

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from typing import Callable
from rapidfuzz import fuzz
from datetime import datetime
from unidecode import unidecode
from sklearn.preprocessing import MinMaxScaler
from .lib_stats import _assignement_stat_combattant

import json
import numpy as np
import re
import pandas as pd
from FightPredixBack.outils import configure_logger


date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_constructeur")


def _ajout_cat_combts(
    caracteristiques: pd.DataFrame, combats: pd.DataFrame
) -> pd.DataFrame:
    """
    Fonction qui assigne les variables catégorielles de chaque combattant
    """

    cat_colonnes_caracteristiques = caracteristiques.select_dtypes(
        include=["object", "bool"]
    ).columns.tolist()
    cat_colonnes_caracteristiques.remove("name")

    def _sub_fonction_differences_cat(
        combattant: str,
        prefixe: str,
        caracteristiques: pd.DataFrame,
        combats: pd.DataFrame,
        index: int,
    ) -> pd.DataFrame:
        stats_combattant = None

        for nom in caracteristiques["name"].values:
            if nom == combattant or fuzz.ratio(nom.lower(), combattant.lower()) >= 90:
                stats_combattant = caracteristiques[
                    caracteristiques["name"] == nom
                ].iloc[0]
                break

        if stats_combattant is not None:
            for col in cat_colonnes_caracteristiques:
                combats.at[index, f"{prefixe}_{col}"] = stats_combattant[col]

        return combats

    for i, combat in combats.iterrows():
        combattant_1 = combat["combattant_1"]
        combattant_2 = combat["combattant_2"]

        combats = _sub_fonction_differences_cat(
            combattant_1, "combattant_1", caracteristiques, combats, i
        )
        combats = _sub_fonction_differences_cat(
            combattant_2, "combattant_2", caracteristiques, combats, i
        )

    return combats


def _difference_num_combats(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction de calcul de la différence entre les caractéristiques des combattants
    au sein de chaque combat.
    """
    combats.reset_index(inplace=True)
    cols_to_drop = []
    colonnes_a_concat = {}

    num_colonnes_combats = combats.select_dtypes(include=["number"]).columns

    pattern = re.compile(r"combattant_(\d+)_(.+)")

    for col in num_colonnes_combats:
        match = pattern.match(col)
        if match:
            stat_type = match.group(2)
            colonnes_a_concat[f"diff_{stat_type}"] = (
                combats[f"combattant_1_{stat_type}"]
                - combats[f"combattant_2_{stat_type}"]
            )
            cols_to_drop.append(f"combattant_1_{stat_type}")
            cols_to_drop.append(f"combattant_2_{stat_type}")

    df_numerique = pd.DataFrame(colonnes_a_concat, index=combats.index)
    if cols_to_drop:
        combats.drop(columns=cols_to_drop, inplace=True, axis=1)
    resultat = pd.concat([combats, df_numerique], axis=1)

    return resultat


def _age_by_DOB(Data: pd.DataFrame):
    """
    Fonction qui calcule l'age des combattants en fonction de leur date de naissance
    """

    data = Data[Data["ÂGE"].isna() & Data["DOB"].notna()]

    for _, cbt in data.iterrows():
        cbt_name = cbt["NAME"].upper()
        dob = data[data["NAME"] == cbt_name]["DOB"].values[0]
        if pd.notna(dob):
            Age = (datetime.now() - datetime.strptime(dob, "%b %d, %Y")).days // 365
            Data.loc[Data["NAME"] == cbt_name, "ÂGE"] = Age
    return Data


def _transformation_debut_octogone(Data: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui transforme la date de debut de l'octogone en nombre de mois
    """
    Data["DÉBUT DE L'OCTOGONE"] = Data["DÉBUT DE L'OCTOGONE"].astype(str)
    Data["DÉBUT DE L'OCTOGONE"] = pd.to_datetime(
        Data["DÉBUT DE L'OCTOGONE"], format="%b. %d, %Y", errors="coerce"
    )
    Data["DÉBUT DE L'OCTOGONE"] = pd.to_numeric(
        (pd.to_datetime("today") - Data["DÉBUT DE L'OCTOGONE"]).dt.days // 30
    ).astype(float)

    return Data


def _nettoyage_nom_colonne(nom: str) -> str:
    return re.sub(r"[^A-Za-z0-9À-ÖØ-öø-ÿ_]+", "_", nom).lower()


def _process_valeur(valeur):
    if pd.isna(valeur) or valeur in ["nan", "None"]:
        return np.nan

    valeur = str(valeur)

    match_percentage = re.match(r"^(\d+)%$", valeur)
    if match_percentage:
        return float(int(match_percentage.group(1)) / 100)

    if "BOUT" in valeur:
        return valeur.split()[0]

    match_time = re.match(r"^(\d+):(\d+)$", valeur)
    if match_time:
        minutes, seconds = map(int, match_time.groups())
        return float(minutes * 60 + seconds)

    if "---" in valeur or "--" in valeur:
        return None

    try:
        return float(valeur)
    except ValueError:
        return valeur


def _process_ratio(valeur):
    """
    Extrait le numérateur et le dénominateur d'une chaîne
    """
    valeur = str(valeur)
    match_ratio = re.match(r"^(\d+)\s+of\s+(\d+)$", valeur)
    if match_ratio:
        num, denom = map(int, match_ratio.groups())
        ratio = round(num / denom, 2) if denom != 0 else np.nan
        return num, denom, ratio


def _cleaning(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui nettoie les données
    """
    new_columns: dict = {}

    Data = data.copy()

    for col in Data.columns:
        if re.match(r"(combattant_1_Fighter|combattant_2_Fighter)", col):
            Data.drop(col, axis=1, inplace=True)
            continue
        if Data[col].dtype == "O":
            ratio_bool = Data[col].apply(
                lambda x: bool(re.match(r"^(\d+)\s+of\s+(\d+)$", str(x)))
            )

            if ratio_bool.any():
                Data[[f"{col}_reussi", f"{col}_total", f"{col}_ratio"]] = Data[
                    col
                ].apply(lambda x: pd.Series(_process_ratio(x)))
                Data.drop(col, axis=1, inplace=True)
                continue

            Data.loc[:, col] = Data[col].apply(_process_valeur)
            try:
                Data[col] = pd.to_numeric(Data[col], errors="raise")
            except ValueError:
                pass

    if new_columns:
        Data = pd.concat([Data, pd.DataFrame(new_columns, index=Data.index)], axis=1)

    return Data


def _sub_fonction_age(
    Data: pd.DataFrame,
    combattant: pd.DataFrame,
    date_combat_annee: datetime,
    ajd: datetime,
) -> int:
    """
    Sous fonction qui calcule l'age des combattants au moment du combat
    """
    for nom in Data["name"].values:
        if fuzz.ratio(nom.lower(), combattant.lower()) >= 90:
            age = Data[Data["name"].str.lower() == nom.lower()]["âge"].values[0]
            dob = Data[Data["name"].str.lower() == nom.lower()]["dob"].values[0]
            if pd.notna(age):
                Age_t = age - (ajd.year - date_combat_annee)
                return Age_t
            elif pd.notna(dob):
                Age_t = date_combat_annee - datetime.strptime(dob, "%b %d, %Y").year
                return Age_t
            else:
                return np.nan
        else:
            return np.nan


def _age_temps_t(caracteristiques: pd.DataFrame, combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui calcul l'age des combattants au moment du combat et l'ajoute dans le dataframe des combats
    """
    Combats = combats.copy()
    for i, combat in Combats.iterrows():
        date_combat_annee = datetime.strptime(
            str(combat["date"]).split(" ")[0].strip(), "%Y-%m-%d"
        ).year
        ajd = datetime.now()
        combattant_1 = combat["combattant_1"]
        combattant_2 = combat["combattant_2"]
        Combats.loc[i, "combattant_1_age_t"] = _sub_fonction_age(
            caracteristiques, combattant_1, date_combat_annee, ajd
        )
        Combats.loc[i, "combattant_2_age_t"] = _sub_fonction_age(
            caracteristiques, combattant_2, date_combat_annee, ajd
        )

    return Combats


def _calcul_victoires_defaites(
    temp_dict: dict,
    cob: pd.DataFrame,
    combattant: str,
    nickname: str,
    prefixe: str,
    resultat: int,
    index: int,
):
    """
    Sous fonction qui calcule les victoires et les défaites des combattants au temps t
    """
    if f"{combattant}_{nickname}_win_t" not in temp_dict:
        temp_dict[f"{combattant}_{nickname}_win_t"] = 0
    if f"{combattant}_{nickname}_losses_t" not in temp_dict:
        temp_dict[f"{combattant}_{nickname}_losses_t"] = 0

    cob.loc[index, f"{prefixe}_win_t"] = temp_dict[f"{combattant}_{nickname}_win_t"]
    cob.loc[index, f"{prefixe}_losses_t"] = temp_dict[
        f"{combattant}_{nickname}_losses_t"
    ]

    if (prefixe == "combattant_1" and resultat == 0) or (
        prefixe == "combattant_2" and resultat == 1
    ):
        temp_dict[f"{combattant}_{nickname}_win_t"] += 1
    elif (prefixe == "combattant_1" and resultat == 1) or (
        prefixe == "combattant_2" and resultat == 0
    ):
        temp_dict[f"{combattant}_{nickname}_losses_t"] += 1


def _calcul_forme_combattant(
    temp_dict: dict,
    cob: pd.DataFrame,
    combattant: str,
    nickname: str,
    prefixe: str,
    resultat: int,
    index: int,
):
    """
    Sous fonction qui calcule la forme des combattants au travers des resultats des 3 derniers combats au temps t de chaque combattant
    """
    if f"{combattant}_{nickname}_forme" not in temp_dict:
        temp_dict[f"{combattant}_{nickname}_forme"] = []

    cob.loc[index, f"{prefixe}_forme"] = sum(
        temp_dict[f"{combattant}_{nickname}_forme"]
    )

    if (prefixe == "combattant_1" and resultat == 0) or (
        prefixe == "combattant_2" and resultat == 1
    ):
        if len(temp_dict[f"{combattant}_{nickname}_forme"]) < 3:
            temp_dict[f"{combattant}_{nickname}_forme"].append(1)
        else:
            temp_dict[f"{combattant}_{nickname}_forme"] = temp_dict[
                f"{combattant}_{nickname}_forme"
            ][1:] + [1]
    elif (prefixe == "combattant_1" and resultat == 1) or (
        prefixe == "combattant_2" and resultat == 0
    ):
        if len(temp_dict[f"{combattant}_{nickname}_forme"]) < 3:
            temp_dict[f"{combattant}_{nickname}_forme"].append(-1)
        else:
            temp_dict[f"{combattant}_{nickname}_forme"] = temp_dict[
                f"{combattant}_{nickname}_forme"
            ][1:] + [-1]


def _calcul_serie_victoires(
    temp_dict: dict,
    cob: pd.DataFrame,
    combattant: str,
    nickname: str,
    prefixe: str,
    resultat: int,
    index: int,
):
    """
    Sous fonction qui calcule la série de victoires des combattants au temps t, dès qu'une defaite est enregistrée la série est remise à 0
    """
    if f"{combattant}_{nickname}_serie" not in temp_dict:
        temp_dict[f"{combattant}_{nickname}_serie"] = []

    cob.loc[index, f"{prefixe}_serie"] = sum(
        temp_dict[f"{combattant}_{nickname}_serie"]
    )

    if (prefixe == "combattant_1" and resultat == 0) or (
        prefixe == "combattant_2" and resultat == 1
    ):
        temp_dict[f"{combattant}_{nickname}_serie"].append(1)
    elif (prefixe == "combattant_1" and resultat == 1) or (
        prefixe == "combattant_2" and resultat == 0
    ):
        temp_dict[f"{combattant}_{nickname}_serie"].clear()


def _calcul_nb_mois_dernier_combat(
    temp_dict: dict,
    cob: pd.DataFrame,
    combattant: str,
    nickname: str,
    prefixe: str,
    date: datetime,
    index: int,
):
    """
    Sous fonction qui calcule le nombre de mois entre le combat actuel d'un combattant et le précedent
    """
    if f"{combattant}_{nickname}_date" not in temp_dict.keys():
        temp_dict[f"{combattant}_{nickname}_date"] = []

    temp_dict[f"{combattant}_{nickname}_date"].append(date)

    if len(temp_dict[f"{combattant}_{nickname}_date"]) > 2:
        temp_dict[f"{combattant}_{nickname}_date"].pop(0)

    cob.loc[index, f"{prefixe}_nb_mois_dernier_combat"] = (
        round(
            (
                temp_dict[f"{combattant}_{nickname}_date"][1]
                - temp_dict[f"{combattant}_{nickname}_date"][0]
            ).days
            / 30
        )
        if len(temp_dict[f"{combattant}_{nickname}_date"]) == 2
        else 0
    )


def _methode_temps_t(Combats: pd.DataFrame) -> pd.DataFrame:
    combats = Combats.copy()
    combats = combats.sort_index(ascending=False)
    temp_dict = {}

    for prefixe in ["combattant_1", "combattant_2"]:
        for methode in ["DEC", "KO/TKO", "SUB", "DQ"]:
            combats[f"{prefixe}_{methode}"] = 0

    for i, combat in combats.iterrows():
        combattant_1, nickname_1 = (
            combat["combattant_1"],
            combat["combattant_1_nickname"],
        )
        combattant_2, nickname_2 = (
            combat["combattant_2"],
            combat["combattant_2_nickname"],
        )
        resultat = combat["resultat"]
        methode = combat["methode"]

        def sub_fonction(combattant, nickname, prefixe, resultat, methode):
            key = f"{combattant}_{nickname}_methode"

            if key not in temp_dict:
                temp_dict[key] = {}

            combats.loc[i, f"{prefixe}_DEC"] = temp_dict[key].get("DEC", 0)
            combats.loc[i, f"{prefixe}_KO/TKO"] = temp_dict[key].get("KO/TKO", 0)
            combats.loc[i, f"{prefixe}_SUB"] = temp_dict[key].get("SUB", 0)
            combats.loc[i, f"{prefixe}_DQ"] = temp_dict[key].get("DQ", 0)

            if (resultat == 0 and prefixe == "combattant_1") or (
                resultat == 1 and prefixe == "combattant_2"
            ):
                if methode in temp_dict[key]:
                    temp_dict[key][methode] += 1
                else:
                    temp_dict[key][methode] = 1

        sub_fonction(combattant_1, nickname_1, "combattant_1", resultat, methode)
        sub_fonction(combattant_2, nickname_2, "combattant_2", resultat, methode)

    combats = combats.sort_index(ascending=True)

    return combats


def _calcul_statistique_generique(
    combats: pd.DataFrame, calculs_par_combattant: Callable, date: bool = False
) -> pd.DataFrame:
    """
    Fonction générique pour calculer des statistiques des combattants à partir des combats.
    """
    cob = combats.copy()
    cob = cob.sort_index(ascending=False)

    temp_dict: dict = {}

    for i, combat in cob.iterrows():
        combattant_1, nickname_1 = (
            combat["combattant_1"],
            combat["combattant_1_nickname"],
        )
        combattant_2, nickname_2 = (
            combat["combattant_2"],
            combat["combattant_2_nickname"],
        )
        if date is False:
            resultat = combat["resultat"]
        else:
            resultat = combat["date"]

        nickname_1 = nickname_1 if isinstance(nickname_1, str) else "NO"
        nickname_2 = nickname_2 if isinstance(nickname_2, str) else "NO"

        calculs_par_combattant(
            temp_dict, cob, combattant_1, nickname_1, "combattant_1", resultat, i
        )
        calculs_par_combattant(
            temp_dict, cob, combattant_2, nickname_2, "combattant_2", resultat, i
        )

    cob = cob.sort_index(ascending=True)
    return cob


def _format_last_stats(
    dico_last_stats: dict, caracteristiques: pd.DataFrame
) -> pd.DataFrame:
    last_stats = pd.DataFrame(dico_last_stats).T
    last_stats.reset_index(inplace=True)
    last_stats.rename(columns={"index": "name"}, inplace=True)
    last_stats.columns = last_stats.columns.str.strip()

    for nom_last_stats in last_stats["name"]:
        for nom_caracteristiques in caracteristiques["name"]:
            if (
                nom_last_stats.lower() == nom_caracteristiques.lower()
                or fuzz.ratio(nom_last_stats.lower(), nom_caracteristiques.lower())
                >= 90
            ):
                last_stats.loc[last_stats["name"] == nom_last_stats, "name"] = (
                    nom_caracteristiques
                )
                break

    return last_stats


def _format_last_stats_nom_identique(
    dico_last_stats_nom_identique: dict, caracteristiques: pd.DataFrame
) -> pd.DataFrame:
    """
    Fonction qui formate les dernières statistiques des combattants à nom identique
    """
    last_stats_nom_identique = pd.DataFrame(dico_last_stats_nom_identique).T
    last_stats_nom_identique.reset_index(inplace=True)
    last_stats_nom_identique.rename(columns={"index": "nickname"}, inplace=True)
    last_stats_nom_identique.columns = last_stats_nom_identique.columns.str.strip()

    for nom_last_stats in last_stats_nom_identique["nickname"]:
        for nom_caracteristiques in caracteristiques["nickname"]:
            if (
                fuzz.ratio(nom_last_stats.lower(), str(nom_caracteristiques).lower())
                >= 90
            ):
                last_stats_nom_identique.loc[
                    last_stats_nom_identique["nickname"] == nom_last_stats, "nickname"
                ] = nom_caracteristiques
                break

    return last_stats_nom_identique


def supprimer_caracteres_speciaux(chaine: str):
    chaine = unidecode(chaine)
    chaine = re.sub(r"[^a-zA-Z0-9\s]", "", chaine)
    chaine = chaine.title()
    return chaine


def _identifier_assignement(
    DataCombats: pd.DataFrame,
    caracteristiques: pd.DataFrame,
    num: int,
    nom_car: str,
    nom_combat: str,
) -> pd.DataFrame:
    """
    Fonction qui assigne les statistiques de taille, poids, reach et portée de la jambe des combattants
    """

    if num == 1:
        liste_caracteristiques = [
            "combattant_1_la_taille",
            "combattant_1_poids",
            "combattant_1_reach",
            "combattant_1_portée_de_la_jambe",
        ]
    elif num == 2:
        liste_caracteristiques = [
            "combattant_2_la_taille",
            "combattant_2_poids",
            "combattant_2_reach",
            "combattant_2_portée_de_la_jambe",
        ]
    else:
        raise ValueError("Le numéro doit être 1 ou 2")

    for car in liste_caracteristiques:
        DataCombats.loc[DataCombats[f"combattant_{num}"] == nom_combat, car] = (
            caracteristiques[caracteristiques["name"] == nom_car][
                car.split(f"{num}_")[1]
            ].values[0]
        )

    return DataCombats


def _attribution_poids(DataCombats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui attribue un poids aux combats
    """

    DataCombats["nb_combat_des_deux_combattants"] = (
        DataCombats["combattant_1_win_t"]
        + DataCombats["combattant_1_losses_t"]
        + DataCombats["combattant_2_win_t"]
        + DataCombats["combattant_2_losses_t"]
    )
    DataCombats = DataCombats[~DataCombats["nb_combat_des_deux_combattants"].isna()]
    DataCombats["poids_ml"] = MinMaxScaler(feature_range=(0.2, 0.8)).fit_transform(
        DataCombats[["nb_combat_des_deux_combattants"]]
    )

    return DataCombats


def _assignement_taille_poids_reach_portee_de_la_jambe(
    DataCombats: pd.DataFrame, caracteristiques: pd.DataFrame
) -> pd.DataFrame:
    for nom in caracteristiques["name"]:
        for c1, c2 in zip(DataCombats["combattant_1"], DataCombats["combattant_2"]):
            if nom.lower() == c1.lower() or fuzz.ratio(c1.lower(), nom.lower()) >= 90:
                DataCombats = _identifier_assignement(
                    DataCombats, caracteristiques, 1, nom, c1
                )
            if nom.lower() == c2.lower() or fuzz.ratio(c2.lower(), nom.lower()) >= 90:
                DataCombats = _identifier_assignement(
                    DataCombats, caracteristiques, 2, nom, c2
                )
    return DataCombats


def _main_constructeur(
    combats: pd.DataFrame, caracteristiques: pd.DataFrame
) -> pd.DataFrame:
    logger.info("Début du constructeur")
    logger.info("Calcule de l'age des combattants")
    caracteristiques = _age_by_DOB(caracteristiques)

    logger.info("Transformation de la date de début de l'octogone")
    caracteristiques = _transformation_debut_octogone(caracteristiques)

    logger.info("Formatage des noms de colonnes")
    caracteristiques.columns = [
        _nettoyage_nom_colonne(col) for col in caracteristiques.columns
    ]

    logger.info("Nettoyage des données")
    combats = _cleaning(data=combats)

    logger.info("Ajout des catégories des combattants")
    combats = _ajout_cat_combts(caracteristiques=caracteristiques, combats=combats)

    logger.info("Calcul des âges des combattants au temps t")
    combats = _age_temps_t(caracteristiques=caracteristiques, combats=combats)

    logger.info("Calcul des statistiques des combattants")
    combats = _calcul_statistique_generique(
        combats=combats, calculs_par_combattant=_calcul_victoires_defaites
    )

    combats = _calcul_statistique_generique(
        combats=combats, calculs_par_combattant=_calcul_forme_combattant
    )

    combats = _calcul_statistique_generique(
        combats=combats, calculs_par_combattant=_calcul_serie_victoires
    )

    combats = _calcul_statistique_generique(
        combats=combats,
        calculs_par_combattant=_calcul_nb_mois_dernier_combat,
        date=True,
    )

    combats = _methode_temps_t(combats)

    with open(
        "FightPredixBack/FightPredixConstructeur/dico_formatage/dico_var.json", "r"
    ) as file:
        dico_var = json.load(file)

    combats.columns = [_nettoyage_nom_colonne(col) for col in combats.columns]
    logger.info("Assignement des statistiques cumulatives des combattants")
    combats, dico_last_stats, dico_last_stats_nom_identique = (
        _assignement_stat_combattant(data=combats, dico_var=dico_var)
    )

    combats = _attribution_poids(combats)

    logger.info("Calcul de la différence entre les caractéristiques des combattants")
    combats = _difference_num_combats(combats)

    last_stats, last_stats_nom_identique = (
        _format_last_stats(
            dico_last_stats=dico_last_stats, caracteristiques=caracteristiques
        ),
        _format_last_stats_nom_identique(
            dico_last_stats_nom_identique=dico_last_stats_nom_identique,
            caracteristiques=caracteristiques,
        ),
    )

    last_stats.to_json(
        "FightPredixBack/FightPredixConstructeur/temp_data/Data_stats_combattants.json",
        orient="records",
    )
    last_stats_nom_identique.to_json(
        "FightPredixBack/FightPredixConstructeur/temp_data/Data_stats_nom_identique.json",
        orient="records",
    )
    combats = _assignement_taille_poids_reach_portee_de_la_jambe(
        combats, caracteristiques
    )
    caracteristiques.columns = [
        _nettoyage_nom_colonne(col) for col in caracteristiques.columns
    ]
    return combats, caracteristiques.merge(last_stats, on="name", how="left")
