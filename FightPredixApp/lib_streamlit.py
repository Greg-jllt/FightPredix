import pandas as pd
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
        "diff_sig_str_total_reussi_moyenne",
        "diff_sig_str_total_total_moyenne",
        "diff_total_str_total_reussi_moyenne",
        "diff_total_str_total_total_moyenne",
        "diff_tdtotal_reussi_moyenne",
        "diff_tdtotal_total_moyenne",
        "diff_headsig_str_total_reussi_moyenne",
        "diff_headsig_str_total_total_moyenne",
        "diff_bodysig_str_total_reussi_moyenne",
        "diff_bodysig_str_total_total_moyenne",
        "diff_legsig_str_total_reussi_moyenne",
        "diff_legsig_str_total_total_moyenne",
        "diff_distancesig_str_total_reussi_moyenne",
        "diff_distancesig_str_total_total_moyenne",
        "diff_clinchsig_str_total_reussi_moyenne",
        "diff_clinchsig_str_total_total_moyenne",
        "diff_groundsig_str_total_reussi_moyenne",
        "diff_groundsig_str_total_total_moyenne",
        "diff_frappe_tete_moyenne",
        "diff_frappe_corps_moyenne",
        "diff_frappe_jambe_moyenne",
        "diff_frappe_distance_moyenne",
        "diff_frappe_clinch_moyenne",
        "diff_frappe_sol_moyenne",
        "diff_kdtotal_moyenne",
        "diff_sig_str_total_ratio_moyenne",
        "diff_total_str_total_ratio_moyenne",
        "diff_tdtotal_ratio_moyenne",
        "diff_sub_atttotal_moyenne",
        "diff_revtotal_moyenne",
        "diff_ctrltotal_moyenne",
        "diff_headsig_str_total_ratio_moyenne",
        "diff_bodysig_str_total_ratio_moyenne",
        "diff_legsig_str_total_ratio_moyenne",
        "diff_distancesig_str_total_ratio_moyenne",
        "diff_clinchsig_str_total_ratio_moyenne",
        "diff_groundsig_str_total_ratio_moyenne",
        "diff_la_taille",
        "diff_poids",
        "diff_reach",
        "diff_portee_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_dec",
        "diff_ko_tko",
        "diff_sub",
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


def _difference_num_combats(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction de calcul de la différence entre les caractéristiques des combattants
    au sein de chaque combat.
    """
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

    df_numerique = pd.DataFrame(colonnes_a_concat, index=combats.index)

    resultat = pd.concat([combats.reset_index(drop=True), df_numerique], axis=1)

    return resultat


def _prediction_streamlit(
    indice_nom1, indice_nom2, DataFighters, num_features, cat_features
):
    predictions: list = []
    for num1, num2 in zip((indice_nom1, indice_nom2), (indice_nom2, indice_nom1)):
        Combattant_1 = pd.DataFrame(DataFighters.loc[num1]).T
        Combattant_2 = pd.DataFrame(DataFighters.loc[num2]).T

        Combattant_1.columns = [
            (
                "combattant_1_" + str(col)
            )
            for col in Combattant_1.columns
        ]
        Combattant_2.columns = [
            (
                "combattant_2_" + str(col)
            )
            for col in Combattant_2.columns
        ]

        Combattant_1["join_key"] = "1"
        Combattant_2["join_key"] = "1"

        combat = Combattant_1.merge(Combattant_2, on="join_key")

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