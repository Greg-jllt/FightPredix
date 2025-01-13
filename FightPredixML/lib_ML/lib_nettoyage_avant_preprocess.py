"""Description

Librairie de nettoyage des données avant le preprocess
"""

import re
import pandas as pd
import miceforest as mf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler


def _supprimer_combattants_problematiques(DataCombats: pd.DataFrame) -> pd.DataFrame:
    """
    On supprime les combattants portant le même nom
    """
    lignes_a_supprimer = pd.concat(
        [
            DataCombats[DataCombats["combattant_1"] == "Bruno Silva"],
            DataCombats[DataCombats["combattant_2"] == "Bruno Silva"],
            DataCombats[DataCombats["combattant_1"] == "Joey Gomez"],
            DataCombats[DataCombats["combattant_2"] == "Joey Gomez"],
            DataCombats[DataCombats["combattant_1"] == "Don Hyun Kim"],
            DataCombats[DataCombats["combattant_2"] == "Don Hyun Kim"],
        ]
    ).index

    return DataCombats.drop(lignes_a_supprimer)


def _garder_combats_apres_2014(DataCombats: pd.DataFrame) -> pd.DataFrame:
    """
    On garde les combats après 2014
    """
    return DataCombats[DataCombats["date"] > "2014-01-01"]


def replace_first_nan(DataCombats: pd.DataFrame) -> pd.DataFrame:
    combattants = set(
        DataCombats["combattant_1"].tolist() + DataCombats["combattant_2"].tolist()
    )
    liste_combattants = list(combattants)

    col_moyenne = [
        col for col in DataCombats.columns if "moyenne" in col and "diff" not in col
    ]

    for nom in liste_combattants:
        data_combattant = pd.concat(
            [
                DataCombats[DataCombats["combattant_1"] == nom][
                    ["combattant_1", "combattant_2"] + col_moyenne
                ],
                DataCombats[DataCombats["combattant_2"] == nom][
                    ["combattant_1", "combattant_2"] + col_moyenne
                ],
            ]
        )

        if data_combattant.shape[0] > 1:
            data_combattant = data_combattant.sort_index(ascending=False)
            data_combattant.reset_index(inplace=True)
            index = data_combattant.loc[0, "index"]

            if data_combattant.loc[0, "combattant_1"] == nom:
                combattant_numero_remplace = "combattant_1"
            else:
                combattant_numero_remplace = "combattant_2"
            col_a_remplacer = [
                col for col in col_moyenne if combattant_numero_remplace in col
            ]

            if data_combattant.loc[1, "combattant_1"] == nom:
                combattant_numero_remplacement = "combattant_1"
            else:
                combattant_numero_remplacement = "combattant_2"

            for col in col_a_remplacer:
                if pd.isna(data_combattant.loc[0, col]):
                    stat_sans_combattant = col.split(combattant_numero_remplace)[1]
                    DataCombats.loc[index, col] = data_combattant.loc[
                        1, f"{combattant_numero_remplacement}{stat_sans_combattant}"
                    ]
    return DataCombats.reset_index(drop=True)


def _impute_dimension_variables(DataCombats: pd.DataFrame) -> pd.DataFrame:
    """
    On impute les valeurs manquantes des variables de dimension (taille, reach, poids, portée de la jambe)
    """

    variable_schema = {
        "combattant_1_la_taille": [
            "combattant_1_poids",
            "combattant_1_reach",
            "combattant_1_portée_de_la_jambe",
        ],
        "combattant_1_poids": [
            "combattant_1_la_taille",
            "combattant_1_reach",
            "combattant_1_portée_de_la_jambe",
        ],
        "combattant_1_reach": [
            "combattant_1_la_taille",
            "combattant_1_poids",
            "combattant_1_portée_de_la_jambe",
        ],
        "combattant_1_portée_de_la_jambe": [
            "combattant_1_la_taille",
            "combattant_1_poids",
            "combattant_1_reach",
        ],
        "combattant_2_la_taille": [
            "combattant_2_poids",
            "combattant_2_reach",
            "combattant_2_portée_de_la_jambe",
        ],
        "combattant_2_poids": [
            "combattant_2_la_taille",
            "combattant_2_reach",
            "combattant_2_portée_de_la_jambe",
        ],
        "combattant_2_reach": [
            "combattant_2_la_taille",
            "combattant_2_poids",
            "combattant_2_portée_de_la_jambe",
        ],
        "combattant_2_portée_de_la_jambe": [
            "combattant_2_la_taille",
            "combattant_2_poids",
            "combattant_2_reach",
        ],
    }

    Data_to_imputation = DataCombats[
        [
            "combattant_1_la_taille",
            "combattant_1_poids",
            "combattant_1_reach",
            "combattant_1_portée_de_la_jambe",
            "combattant_2_la_taille",
            "combattant_2_poids",
            "combattant_2_reach",
            "combattant_2_portée_de_la_jambe",
        ]
    ]

    imputation_model = mf.ImputationKernel(
        data=Data_to_imputation,
        variable_schema=variable_schema,
        imputation_order="ascending",
        mean_match_strategy="shap",
        initialize_empty=True,
        save_all_iterations_data=True,
        random_state=42,
    )

    imputation_model.mice(3)
    Data_to_imputation = imputation_model.complete_data()

    DataCombats[
        [
            "combattant_1_la_taille",
            "combattant_1_poids",
            "combattant_1_reach",
            "combattant_1_portée_de_la_jambe",
            "combattant_2_la_taille",
            "combattant_2_poids",
            "combattant_2_reach",
            "combattant_2_portée_de_la_jambe",
        ]
    ] = imputation_model.complete_data()

    return DataCombats


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
            round(
                (
                    datetime.strptime(
                        temp_dict[f"{combattant}_{nickname}_date"][1], "%Y-%m-%d"
                    )
                    - datetime.strptime(
                        temp_dict[f"{combattant}_{nickname}_date"][0], "%Y-%m-%d"
                    )
                ).days
                / 30
            )
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
        "diff_portée_de_la_jambe",
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
        "combattant_2_country_of_birth_tapology",
    ]

    output_feature = ["resultat", "poids_ml"]

    return numeric_features, categorical_features, output_feature


def _main_nettoyage() -> pd.DataFrame:
    DataCombats = pd.read_csv("./Data/Data_final_combats_V.csv")

    DataCombats = _supprimer_combattants_problematiques(DataCombats)

    DataCombats = _garder_combats_apres_2014(DataCombats)
    DataCombats = replace_first_nan(DataCombats)
    DataCombats = _impute_dimension_variables(DataCombats)
    DataCombats = _calcul_nb_mois_dernier_combat(DataCombats)
    DataCombats = _attribution_poids(DataCombats)

    liste_diff = [col for col in DataCombats.columns if "diff" in col]
    DataCombats.drop(columns=liste_diff, inplace=True)
    DataCombats = _difference_num_combats(DataCombats)

    numeric_features, categorical_features, output_feature = _liste_features()

    DataCombats = DataCombats.rename(
        columns={
            "style_de_combat_1": "combattant_1_style_de_combat",
            "style_de_combat_2": "combattant_2_style_de_combat",
            "country_of_residence_tapology_1": "combattant_1_country_of_residence_tapology",
            "country_of_residence_tapology_2": "combattant_2_country_of_residence_tapology",
            "country_of_birth_tapology_1": "combattant_1_country_of_birth_tapology",
            "country_of_birth_tapology_2": "combattant_2_country_of_birth_tapology",
        }
    )

    Data_for_ml = DataCombats[numeric_features + categorical_features + output_feature]

    return Data_for_ml


if __name__ == "__main__":
    _main_nettoyage()
