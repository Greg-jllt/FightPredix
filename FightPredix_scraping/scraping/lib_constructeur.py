"""
Librairie de fonctions pour la construction de la base de données
Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from rapidfuzz import fuzz
from datetime import datetime
from .lib_stats import _assignement_stat_combattant
from unidecode import unidecode
import json
import numpy as np
import re
import pandas as pd


def _difference_cat_combts(
    caracteristiques: pd.DataFrame, combats: pd.DataFrame
) -> pd.DataFrame:
    lignes_a_ajouter = []
    cat_colonnes_caracteristiques = caracteristiques.select_dtypes(
        include=["object"]
    ).columns.tolist()
    cat_colonnes_caracteristiques.remove("name")

    for i, combat in combats.iterrows():
        combattant_1 = combat["combattant_1"]
        combattant_2 = combat["combattant_2"]

        stats_combattant_1, stats_combattant_2 = None, None

        for nom in caracteristiques["name"].values:
            if fuzz.ratio(nom.lower(), combattant_1.lower()) >= 90:
                stats_combattant_1 = caracteristiques[
                    caracteristiques["name"] == nom
                ].iloc[0]
                break

        for nom in caracteristiques["name"].values:
            if fuzz.ratio(nom.lower(), combattant_2.lower()) >= 90:
                stats_combattant_2 = caracteristiques[
                    caracteristiques["name"] == nom
                ].iloc[0]
                break

        if stats_combattant_1 is not None and stats_combattant_2 is not None:
            nouvelle_ligne = {"index": i}

            for col in cat_colonnes_caracteristiques:
                nouvelle_ligne[f"{col}_1"] = stats_combattant_1[col]
                nouvelle_ligne[f"{col}_2"] = stats_combattant_2[col]

            lignes_a_ajouter.append(nouvelle_ligne)

    df_categoriel = (
        pd.DataFrame(lignes_a_ajouter).set_index("index")
        if lignes_a_ajouter
        else pd.DataFrame()
    )

    resultat = pd.concat([combats.reset_index(drop=True), df_categoriel], axis=1)

    return resultat


def _difference_num_combats(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction de calcul de la différence entre les caractéristiques des combattants
    au sein de chaque combat.
    """

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

    resultat = pd.concat([combats.reset_index(drop=True), df_numerique], axis=1)

    # if cols_to_drop:
    #     Console().print(f"Colonnes à supprimer : {len(cols_to_drop)}")
    #     resultat.drop(cols_to_drop, axis=1, inplace=True)

    return resultat


def _age_by_DOB(Data):
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


def _transformation_debut_octogone(data):
    """
    Fonction qui transforme la date de debut de l'octogone en nombre de mois
    """
    data["DÉBUT DE L'OCTOGONE"] = data["DÉBUT DE L'OCTOGONE"].astype(str)
    data["DÉBUT DE L'OCTOGONE"] = pd.to_datetime(
        data["DÉBUT DE L'OCTOGONE"], format="%b. %d, %Y", errors="coerce"
    )
    data["DÉBUT DE L'OCTOGONE"] = pd.to_numeric(
        (pd.to_datetime("today") - data["DÉBUT DE L'OCTOGONE"]).dt.days // 30
    ).astype(float)

    return data


def _clean_column_nom(nom):
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


def _cleaning(data):
    """
    Fonction qui nettoie les données
    """
    new_columns = {}

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


def _sub_fonction_age(Data, combattant, date_combat_annee, ajd):
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


def _age_temps_t(Data: pd.DataFrame, combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui calcul l'age des combattants au moment du combat et l'ajoute dans le dataframe des combats
    """
    Combats = combats.copy()
    for i, combat in Combats.iterrows():
        date_combat_annee = pd.to_datetime(
            datetime.strptime(combat["date"], "%B %d, %Y")
        ).year
        ajd = datetime.now()
        combattant_1 = combat["combattant_1"]
        combattant_2 = combat["combattant_2"]

        Combats.loc[i, "combattant_1_age_t"] = _sub_fonction_age(
            Data, combattant_1, date_combat_annee, ajd
        )
        Combats.loc[i, "combattant_2_age_t"] = _sub_fonction_age(
            Data, combattant_2, date_combat_annee, ajd
        )

    return Combats


def _calcul_statistique_generique(
    combats: pd.DataFrame, calculs_par_combattant
) -> pd.DataFrame:
    """
    Fonction générique pour calculer des statistiques des combattants à partir des combats.
    """
    cob = combats.copy()
    cob = cob.sort_index(ascending=False)

    temp_dict: dict = {}

    for i, combat in cob.iterrows():
        combattant_1, nickname_1 = combat["combattant_1"], combat["nickname_1"]
        combattant_2, nickname_2 = combat["combattant_2"], combat["nickname_2"]
        resultat = combat["resultat"]

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


def _calcul_victoires_defaites(
    temp_dict, cob, combattant, nickname, prefixe, resultat, index
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
    temp_dict, cob, combattant, nickname, prefixe, resultat, index
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
    temp_dict, cob, combattant, nickname, prefixe, resultat, index
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


def _format_last_stats(dico_last_stats: dict) -> pd.DataFrame:
    last_stats = pd.DataFrame(dico_last_stats).T
    last_stats.reset_index(inplace=True)
    last_stats.rename(columns={"index": "name"}, inplace=True)
    last_stats.columns = last_stats.columns.str.strip()
    return last_stats


def _format_last_stats_nom_identique(
    dico_last_stats_nom_identique: dict,
) -> pd.DataFrame:
    """
    Fonction qui formate les dernières statistiques des combattants à nom identique
    """
    last_stats_nom_identique = pd.DataFrame(dico_last_stats_nom_identique).T
    last_stats_nom_identique.reset_index(inplace=True)
    last_stats_nom_identique.rename(columns={"index": "nickname"}, inplace=True)
    last_stats_nom_identique.columns = last_stats_nom_identique.columns.str.strip()
    return last_stats_nom_identique


def supprimer_caracteres_speciaux(chaine):
    chaine = unidecode(chaine)
    chaine = re.sub(r"[^a-zA-Z0-9\s]", "", chaine)
    chaine = chaine.title()
    return chaine


def _title_holder_creation(
    DataCombats: pd.DataFrame, DataFighters: pd.DataFrame
) -> pd.DataFrame:
    """
    Fonction qui crée une colonne indiquant si le combattant est détenteur d'un titre
    """
    liste_combattants = list(
        set(DataCombats["combattant_1"].tolist() + DataCombats["combattant_2"].tolist())
    )

    DataCombats["title_holder_1"] = 0
    DataCombats["title_holder_2"] = 0

    for nom in liste_combattants:
        if not DataFighters[DataFighters["name"] == nom]["title_holder"].empty:
            if DataFighters[DataFighters["name"] == nom]["title_holder"].values[0]:
                DataCombats.loc[
                    DataCombats["combattant_1"] == nom, "title_holder_1"
                ] = 1
                DataCombats.loc[
                    DataCombats["combattant_2"] == nom, "title_holder_2"
                ] = 1

    return DataCombats


def _main_construct(
    combats: pd.DataFrame, caracteristiques: pd.DataFrame
) -> pd.DataFrame:
    caracteristiques = _age_by_DOB(caracteristiques)

    caracteristiques = _transformation_debut_octogone(caracteristiques)

    caracteristiques.columns = [
        _clean_column_nom(col) for col in caracteristiques.columns
    ]

    combats = _cleaning(combats)
    combats = _difference_cat_combts(caracteristiques, combats)
    combats = _age_temps_t(caracteristiques, combats)
    combats = _calcul_statistique_generique(combats, _calcul_victoires_defaites)
    combats = _calcul_statistique_generique(combats, _calcul_forme_combattant)
    combats = _calcul_statistique_generique(combats, _calcul_serie_victoires)

    with open(
        "FightPredix_scraping/scraping/dico_formatage/dico_var.json", "r"
    ) as file:
        dico_var = json.load(file)

    combats, dico_last_stats, dico_last_stats_nom_identique = (
        _assignement_stat_combattant(combats, dico_var)
    )
    combats = _difference_num_combats(combats)
    last_stats, last_stats_nom_identique = (
        _format_last_stats(dico_last_stats),
        _format_last_stats_nom_identique(dico_last_stats_nom_identique),
    )
    caracteristiques["name"] = [
        supprimer_caracteres_speciaux(nom) for nom in caracteristiques["name"]
    ]
    last_stats_nom_identique.to_csv("data/Data_stats_nom_identique.csv", index=False)
    combats = _derniere_difference(combats, caracteristiques)
    combats = _title_holder_creation(combats, caracteristiques)
    return combats, caracteristiques.merge(last_stats, on="name", how="left")


def _derniere_difference(
    DataCombats: pd.DataFrame, DataFighters: pd.DataFrame
) -> pd.DataFrame:
    for nom in DataFighters["name"]:
        for c1, c2 in zip(DataCombats["combattant_1"], DataCombats["combattant_2"]):
            if nom == c1:
                DataCombats.loc[
                    DataCombats["combattant_1"] == nom, "combattant_1_la_taille"
                ] = DataFighters[DataFighters["name"] == nom]["la_taille"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_1"] == nom, "combattant_1_poids"
                ] = DataFighters[DataFighters["name"] == nom]["poids"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_1"] == nom, "combattant_1_reach"
                ] = DataFighters[DataFighters["name"] == nom]["reach"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_1"] == nom,
                    "combattant_1_portée_de_la_jambe",
                ] = DataFighters[DataFighters["name"] == nom][
                    "portée_de_la_jambe"
                ].values[
                    0
                ]
            if nom == c2:
                DataCombats.loc[
                    DataCombats["combattant_2"] == nom, "combattant_2_la_taille"
                ] = DataFighters[DataFighters["name"] == nom]["la_taille"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_2"] == nom, "combattant_2_poids"
                ] = DataFighters[DataFighters["name"] == nom]["poids"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_2"] == nom, "combattant_2_reach"
                ] = DataFighters[DataFighters["name"] == nom]["reach"].values[0]
                DataCombats.loc[
                    DataCombats["combattant_2"] == nom,
                    "combattant_2_portée_de_la_jambe",
                ] = DataFighters[DataFighters["name"] == nom][
                    "portée_de_la_jambe"
                ].values[
                    0
                ]

    DataCombats["diff_la_taille"] = (
        DataCombats["combattant_1_la_taille"] - DataCombats["combattant_2_la_taille"]
    )
    DataCombats["diff_poids"] = (
        DataCombats["combattant_1_poids"] - DataCombats["combattant_2_poids"]
    )
    DataCombats["diff_reach"] = (
        DataCombats["combattant_1_reach"] - DataCombats["combattant_2_reach"]
    )
    DataCombats["diff_portée_de_la_jambe"] = (
        DataCombats["combattant_1_portée_de_la_jambe"]
        - DataCombats["combattant_2_portée_de_la_jambe"]
    )
    return DataCombats


if __name__ == "__main__":
    caracteristiques = pd.read_csv("data/Data_ufc_fighters.csv")
    combats = pd.read_csv("data/Data_ufc_stats_combats.csv")

    caracteristiques = _main_construct(
        combats=combats, caracteristiques=caracteristiques
    )

    caracteristiques.to_csv("data/Data_jointes_complet_actuel.csv", index=False)
    combats.to_csv("data/Data_ufc_combats_cplt.csv", index=False)
