"""Description

Ce module vise à préparer les données de tests et d'entraînement pour les modèles de machine learning
"""

import pandas as pd
from sklearn.model_selection import train_test_split


def _creer_x_y(
    Data: pd.DataFrame, variable_a_predire: str, variable_de_poids: str
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Cette fonction permet de créer les variables explicatives et la variable cible
    A noter que nous plaçons la variable de poids dans y avec la variable cible
    """
    X = Data.drop([variable_a_predire, variable_de_poids], axis=1)
    y = Data[[variable_a_predire, variable_de_poids]]
    return X, y


def _symetrisation_explicative(
    X: pd.DataFrame, num_features: list[str], cat_features: list[str]
) -> pd.DataFrame:
    """
    Cette fonction permet de symétriser les données explicatives
    Elle inverse les valeurs des variables numériques et les combattants
    Elle inverse également les valeurs des variables catégorielles
    """

    X_new = X.copy()

    for col in num_features:
        X_new[col] = X_new[col].apply(lambda x: -x)

    feature_sans_combattant = [
        col.split("combattant_1")[1] for col in cat_features if "combattant_1" in col
    ]
    for col in feature_sans_combattant:
        X_new[f"combattant_1{col}"], X_new[f"combattant_2{col}"] = (
            X_new[f"combattant_2{col}"],
            X_new[f"combattant_1{col}"],
        )

    return pd.concat([X, X_new], axis=0).reset_index(drop=True)


def _symetrisation_resultat_du_combat(y: pd.DataFrame) -> pd.DataFrame:
    """
    Cette fonction permet de symétriser les données de la variable cible
    """

    y_new = y.copy()
    y_new["resultat"] = y_new["resultat"].apply(lambda x: 1 if x == 0 else 0)
    return pd.concat([y, y_new], axis=0).reset_index(drop=True)


def _preparer_echantillons(
    Data: pd.DataFrame,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Cette fonction permet de préparer les données de tests et d'entraînement
    """

    X, y = _creer_x_y(Data, variable_a_predire, variable_de_poids)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    X_train, X_test = (
        _symetrisation_explicative(
            X_train, variables_numeriques, variables_categorielles
        ),
        _symetrisation_explicative(
            X_test, variables_numeriques, variables_categorielles
        ),
    )
    y_train, y_test = (
        _symetrisation_resultat_du_combat(y_train),
        _symetrisation_resultat_du_combat(y_test),
    )

    return X_train, X_test, y_train, y_test
