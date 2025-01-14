"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour la régression logistique
"""

from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_selection import VarianceThreshold, SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from joblib import parallel_backend
from sklearn.decomposition import PCA
from typing import Union


def _pipeline_regression_logistique(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
    param_grid: dict,
) -> dict[str, Union[str, Pipeline, float]]:
    """
    Cette fonction crée un pipeline dans le but d'optimiser les résultats de la régression logistique
    """

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        (
                            "Suppress_low_var",
                            VarianceThreshold(threshold=(0.9 * (1 - 0.9))),
                        ),
                        ("knn_imputer", KNNImputer()),
                        ("standard_scaler", StandardScaler()),
                        ("PCA", PCA(random_state=42)),
                    ]
                ),
                variables_numeriques,
            ),
            (
                "cat",
                Pipeline(
                    [
                        (
                            "simple_imputer",
                            SimpleImputer(
                                strategy="constant", fill_value="non-renseigné"
                            ),
                        ),
                        ("onehot_encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                variables_categorielles,
            ),
        ]
    )

    pipe = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "feature_selection_random_forest",
                SelectFromModel(
                    estimator=RandomForestClassifier(n_estimators=400, random_state=42)
                ),
            ),
            ("regression_logistique", LogisticRegression()),
        ]
    )

    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, n_jobs=-1, pre_dispatch="2*n_jobs"
    )
    with parallel_backend("loky"):
        grid_search.fit(
            X_train,
            y_train[variable_a_predire],
            regression_logistique__sample_weight=y_train[variable_de_poids],
        )

    return dict(
        nom="Régression logistique",
        modele=grid_search.best_estimator_,
        score_entrainement=grid_search.best_score_,
    )
