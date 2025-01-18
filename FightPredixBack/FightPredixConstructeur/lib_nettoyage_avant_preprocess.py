"""Description

Librairie de nettoyage des données avant le preprocess
"""

import re
import pandas as pd
import miceforest as mf
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

    variables_numeriques = [
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
        "diff_sig_str_percent_total_moyenne",
        "diff_total_str_total_ratio_moyenne",
        "diff_tdtotal_ratio_moyenne",
        "diff_td_percent_total_moyenne",
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
        "diff_portée_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_sub",
        "diff_ko_tko",
        "diff_dec",
    ]

    variables_categorielles = [
        "combattant_1_style_de_combat",
        "combattant_2_style_de_combat",
        "combattant_1_country_of_residence_tapology",
        "combattant_2_country_of_residence_tapology",
        "combattant_1_country_of_birth_tapology",
        "combattant_2_country_of_birth_tapology",
    ]

    variable_a_predire = "resultat"

    variable_de_poids = "poids_ml"

    return (
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    )


def _suppress_nan(
    DataCombats: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, str]:
    """
    Cette fonction effectue les derniers ajustements sur les données avant de les passer dans le modèle.
    supprime les colonnes avec plus de 30% de valeurs manquantes
    supprime les lignes avec plus de 40% de valeurs manquantes
    """

    DataCombats.dropna(thresh=0.65 * DataCombats.shape[1], inplace=True)
    size = DataCombats.shape
    nan_values = DataCombats.isna().sum()
    nan_values = nan_values.sort_values(ascending=True) * 100 / size[0]
    num_features, cat_features, output_features = _liste_features()
    if (
        len(
            [
                col
                for col in DataCombats.columns
                if nan_values[col] > 30 and col in num_features
            ]
        )
        > 0
    ):
        num_features.remove(
            *[
                col
                for col in DataCombats.columns
                if nan_values[col] > 30 and col in num_features
            ]
        )

    if (
        len(
            [
                col
                for col in DataCombats.columns
                if nan_values[col] > 30 and col in cat_features
            ]
        )
        > 0
    ):
        cat_features.remove(
            *[
                col
                for col in DataCombats.columns
                if nan_values[col] > 30 and col in cat_features
            ]
        )

    return DataCombats


def _main_nettoyage_avant_preprocess(DataCombats: pd.DataFrame) -> pd.DataFrame:
    """
    Cette fonction effectue les derniers ajustements sur les données avant de les passer dans le modèle.
    """

    DataCombats = _supprimer_combattants_problematiques(DataCombats)
    DataCombats = _garder_combats_apres_2014(DataCombats).reset_index(drop=True)
    DataCombats = _impute_dimension_variables(DataCombats)
    DataCombats = _attribution_poids(DataCombats)

    DataCombats.drop(
        columns=[col for col in DataCombats.columns if "diff" in col], inplace=True
    )
    DataCombats = _difference_num_combats(DataCombats)

    (
        variables_numeriques,
        variables_categorielles,
        variable_a_predire,
        variable_de_poids,
    ) = _liste_features()

    DataCombats = DataCombats[
        variables_numeriques
        + variables_categorielles
        + variable_a_predire
        + variable_de_poids
    ]
    DataCombats = _suppress_nan(DataCombats)
    DataCombats.rename(
        columns={"diff_portée_de_la_jambe": "diff_portee_de_la_jambe"},
        axis=1,
        inplace=True,
    )
    return DataCombats
