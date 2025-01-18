from datetime import datetime
import pandas as pd
from rapidfuzz import fuzz
from PIL import Image

import joblib
import requests
import re
import os 


def _liste_features() -> tuple[list[str], list[str], list[str]]:
    """
    Renvoie des listes de variables utilisables pour le machine learning
    """

    numeric_features = [
        "diff_age_t",
        "diff_win_t",
        "diff_losses_t",
        "diff_forme",
        "diff_serie",
        "diff_Sig_str_total_reussi_moyenne",
        "diff_Sig_str_total_total_moyenne",
        "diff_Total_str_total_reussi_moyenne",
        "diff_Total_str_total_total_moyenne",
        "diff_Tdtotal_reussi_moyenne",
        "diff_Tdtotal_total_moyenne",
        "diff_Headsig_str_total_reussi_moyenne",
        "diff_Headsig_str_total_total_moyenne",
        "diff_Bodysig_str_total_reussi_moyenne",
        "diff_Bodysig_str_total_total_moyenne",
        "diff_Legsig_str_total_reussi_moyenne",
        "diff_Legsig_str_total_total_moyenne",
        "diff_Distancesig_str_total_reussi_moyenne",
        "diff_Distancesig_str_total_total_moyenne",
        "diff_Clinchsig_str_total_reussi_moyenne",
        "diff_Clinchsig_str_total_total_moyenne",
        "diff_Groundsig_str_total_reussi_moyenne",
        "diff_Groundsig_str_total_total_moyenne",
        "diff_frappe_tete_moyenne",
        "diff_frappe_corps_moyenne",
        "diff_frappe_jambe_moyenne",
        "diff_frappe_distance_moyenne",
        "diff_frappe_clinch_moyenne",
        "diff_frappe_sol_moyenne",
        "diff_KDtotal_moyenne",
        "diff_Sig_str_total_ratio_moyenne",
        "diff_Sig_str_percent_total_moyenne",
        "diff_Total_str_total_ratio_moyenne",
        "diff_Tdtotal_ratio_moyenne",
        "diff_Td_percent_total_moyenne",
        "diff_Sub_atttotal_moyenne",
        "diff_Revtotal_moyenne",
        "diff_Ctrltotal_moyenne",
        "diff_Headsig_str_total_ratio_moyenne",
        "diff_Bodysig_str_total_ratio_moyenne",
        "diff_Legsig_str_total_ratio_moyenne",
        "diff_Distancesig_str_total_ratio_moyenne",
        "diff_Clinchsig_str_total_ratio_moyenne",
        "diff_Groundsig_str_total_ratio_moyenne",
        "diff_la_taille",
        "diff_poids",
        "diff_reach",
        "diff_portee_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_DEC",
        "diff_KO/TKO",
        "diff_SUB",
    ]

    categorical_features = [
        "combattant_1_style_de_combat",
        "combattant_2_style_de_combat",
        "combattant_1_country_of_residence_tapology",
        "combattant_2_country_of_residence_tapology",
        "combattant_1_country_of_birth_tapology",
        "combattant_2_country_of_birth_tapology"
    ]

    output_feature = ["resultat", "poids_ml"]

    return numeric_features, categorical_features, output_feature


def _calcul_nb_mois_dernier_combat(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui calcule les victoires des combattants au moment du combat
    """
    cob = combats.copy()
    cob = cob.sort_index(ascending=False)

    temp_dict: dict = {}

    def _sub_nb_mois_dernier_combat(combattant, nickname, prefixe):
        if f"{combattant}_{nickname}_date" not in temp_dict.keys():
            temp_dict[f"{combattant}_{nickname}_date"] = []

        temp_dict[f"{combattant}_{nickname}_date"].append(date)

        if len(temp_dict[f"{combattant}_{nickname}_date"]) > 2:
            temp_dict[f"{combattant}_{nickname}_date"].pop(0)

        cob.loc[i, f"{prefixe}_nb_mois_dernier_combat"] = (
            round((temp_dict[f"{combattant}_{nickname}_date"][1] - temp_dict[f"{combattant}_{nickname}_date"][0]).days / 30)
            if len(temp_dict[f"{combattant}_{nickname}_date"]) == 2
            else 0
        )
 
    for i, combat in cob.iterrows():
        combattant_1, nickname_1 = combat["combattant_1"], combats["nickname_1"]
        combattant_2, nickname_2 = combat["combattant_2"], combats["nickname_2"]
        date = combat["date"]

        nickname_1 = nickname_1 if isinstance(nickname_1, str) else "NO"
        nickname_2 = nickname_2 if isinstance(nickname_2, str) else "NO"

        _sub_nb_mois_dernier_combat(combattant_1, nickname_1, "combattant_1")
        _sub_nb_mois_dernier_combat(combattant_2, nickname_2, "combattant_2")

    cob = cob.sort_index(ascending=True)

    return cob

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


def _sub_fonction_cherche_metrique(nom, c1, c2, Data_combattant, DataCombats):
    if nom.lower() == c1.lower() or fuzz.ratio(nom.lower(), c1.lower()) >= 90:
        Data_combattant = pd.concat(
            [Data_combattant, DataCombats[DataCombats["combattant_1"] == c1]]
        )

    if nom.lower() == c2.lower() or fuzz.ratio(nom.lower(), c2.lower()) >= 90:
        Data_combattant = pd.concat(
            [Data_combattant, DataCombats[DataCombats["combattant_2"] == c2]]
        )

    return Data_combattant


def _obtenir_statistiques_combattant(nom, data_combattant):
    """
    Cherche et retourne les statistiques d'un combattant dans un DataFrame.
    """
    for suffixe in ["1", "2"]:
        if f"combattant_{suffixe}" in data_combattant.columns and (
            nom.lower() == data_combattant[f"combattant_{suffixe}"].iloc[0].lower()
            or fuzz.ratio(
                nom.lower(), data_combattant[f"combattant_{suffixe}"].iloc[0].lower()
            )
            >= 90
        ):
            return (
                data_combattant[f"combattant_{suffixe}_forme"].iloc[0],
                data_combattant[f"combattant_{suffixe}_serie"].iloc[0],
                data_combattant[f"combattant_{suffixe}_nb_mois_dernier_combat"].iloc[0],
            )
    return None, None, None


def _prediction_streamlit(
    indice_nom1, indice_nom2, DataFighters, DataCombats, num_features, cat_features
):
    predictions: list = []
    for num1, num2 in zip((indice_nom1, indice_nom2), (indice_nom2, indice_nom1)):
        Combattant_1 = pd.DataFrame(DataFighters.loc[num1]).T
        Combattant_2 = pd.DataFrame(DataFighters.loc[num2]).T

        Combattant_1.columns = [
            (
                "combattant_1" + str(col)
                if "moyenne" in col
                else "combattant_1_" + str(col)
            )
            for col in Combattant_1.columns
        ]
        Combattant_2.columns = [
            (
                "combattant_2" + str(col)
                if "moyenne" in col
                else "combattant_2_" + str(col)
            )
            for col in Combattant_2.columns
        ]

        Combattant_1["join_key"] = "1"
        Combattant_2["join_key"] = "1"

        combat = Combattant_1.merge(Combattant_2, on="join_key")
        Data_combattant_1 = pd.DataFrame()
        Data_combattant_2 = pd.DataFrame()

        nom1 = DataFighters.loc[num1, "name"]
        nom2 = DataFighters.loc[num2, "name"]

        for c1, c2 in zip(DataCombats["combattant_1"], DataCombats["combattant_2"]):

            Data_combattant_1 = _sub_fonction_cherche_metrique(
                nom1, c1, c2, Data_combattant_1, DataCombats=DataCombats
            )
            Data_combattant_2 = _sub_fonction_cherche_metrique(
                nom2, c1, c2, Data_combattant_2, DataCombats=DataCombats
            )

            if Data_combattant_1.shape[0] > 0 and Data_combattant_2.shape[0] > 0:
                break

        combattant_1_forme, combattant_1_serie, combattant_1_nb_mois = (
            _obtenir_statistiques_combattant(nom1, Data_combattant_1)
        )
        combattant_2_forme, combattant_2_serie, combattant_2_nb_mois = (
            _obtenir_statistiques_combattant(nom2, Data_combattant_2)
        )

        combat.loc[0, "combattant_1_forme"] = combattant_1_forme
        combat.loc[0, "combattant_1_serie"] = combattant_1_serie
        combat.loc[0, "combattant_1_nb_mois_dernier_combat"] = combattant_1_nb_mois
        combat.loc[0, "combattant_2_forme"] = combattant_2_forme
        combat.loc[0, "combattant_2_serie"] = combattant_2_serie
        combat.loc[0, "combattant_2_nb_mois_dernier_combat"] = combattant_2_nb_mois

        var_moyenne = [col for col in combat.columns if "moyenne" in col]

            var_num_en_plus = [
                "combattant_1_win",
                "combattant_1_losses",
                "combattant_1_age",
                "combattant_1_la_taille",
                "combattant_1_poids",
                "combattant_1_reach",
                "combattant_1_portee_de_la_jambe",
                "combattant_2_win",
                "combattant_2_losses",
                "combattant_2_age",
                "combattant_2_la_taille",
                "combattant_2_poids",
                "combattant_2_reach",
                "combattant_2_portee_de_la_jambe",
                "combattant_1_sol",
                "combattant_1_ko_tko",
                "combattant_1_dec",
                "combattant_1_sub",
                "combattant_2_sol",
                "combattant_2_ko_tko",
                "combattant_2_dec",
                "combattant_2_sub",
                "combattant_1_forme",
                "combattant_1_serie",
                "combattant_2_forme",
                "combattant_2_serie",
                "combattant_1_nb_mois_dernier_combat",
                "combattant_2_nb_mois_dernier_combat",
            ]

            cat_features = [
                "combattant_1_style_de_combat",
                "combattant_1_country_of_residence_tapology",
                "combattant_1_country_of_birth_tapology",
                "combattant_2_style_de_combat",
                "combattant_2_country_of_residence_tapology",
                "combattant_2_country_of_birth_tapology",
            ]
            
            liste_a_travailler = var_moyenne + var_num_en_plus + cat_features

            combat = combat[liste_a_travailler]
            
            type_mapping = {col: 'number' if col in var_num_en_plus + var_moyenne else 'object' for col in combat.columns}

        for col, dtype in type_mapping.items():
            if dtype == "number":
                combat[col] = combat[col].astype(
                    float
                )  # Convertir en float pour les colonnes numériques
            else:
                combat[col] = combat[col].astype(
                    str
                )  # Convertir en string pour les colonnes catégorielles

        combat = _difference_num_combats(combat)

        combat.rename(
            columns={
                "diff_age": "diff_age_t",
                "diff_win": "diff_win_t",
                "diff_losses": "diff_losses_t",
                "diff_dec": "diff_DEC",
                "diff_ko_tko": "diff_KO/TKO",
                "diff_sub": "diff_SUB",
            },
            inplace=True,
        )

        modele_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "ModelApp", "best_model.pkl"
        )
        model = joblib.load(modele_path)

        predictions.append(model.predict_proba(combat[num_features + cat_features]))

    results = ((predictions[1].flatten()[1] + predictions[0].flatten()[0])/2 , (predictions[1].flatten()[0] + predictions[0].flatten()[1])/2)

    return results

def _download_et_convert_image(url, filename):
    if not os.path.exists('img'):
        os.makedirs('img')

    if url != "None":
        with open(filename, 'wb') as handle:
            response = requests.get(url, stream=True)
            if not response.ok: 
                print(response)
                return None
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        if os.path.exists(filename):
            im = Image.open(filename)
            png_filename = filename.replace('.jpg', '.png')
            im.save(png_filename)
            os.remove(filename)
            return png_filename
    return None