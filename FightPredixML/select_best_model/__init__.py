def _liste_features() -> tuple[list[str], list[str], str, str]:
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
        "diff_portee_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_dec",
        "diff_ko/tko",
        "diff_sub",
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
    
class ModelOptmizationError(Exception):
    """Exception levée lorsque l'optimisation du modèle échoue"""
    def __init__(self, message: str):
        super().__init__(message)