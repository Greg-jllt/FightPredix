"""Description

Dernier des nettoyages des variables explicatives avant envoi au preprocessing
"""

import pandas as pd
from .lib_nettoyage_avant_preprocess import _liste_features


def _main_process_avant_model(
    DataCombats: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, str]:
    """
    Cette fonction effectue les derniers ajustements sur les données avant de les passer dans le modèle.
    """

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

    X, y = DataCombats[num_features + cat_features], DataCombats["resultat"]

    return X, y, output_features[1]
