"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour le modèle de réseau de neurones
"""

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, VarianceThreshold
from sklearn.feature_selection import SelectFromModel
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from joblib import parallel_backend
from sklearn.decomposition import PCA
import numpy as np


def _pipeline(
    X: pd.DataFrame, y: pd.Series, num_features: list[str], cat_features: list[str]
) -> tuple[ColumnTransformer, Pipeline]:
    """
    Cette fonction crée un pipeline pour le préprocess des données
    """

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

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
                        ("imputer", KNNImputer()),
                        ("scaler", StandardScaler()),
                        ("pca", PCA(random_state=42)),
                    ]
                ),
                num_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        (
                            "imputer",
                            # SimpleImputer(strategy='most_frequent'),
                            SimpleImputer(
                                strategy="constant", fill_value="non-renseigné"
                            ),
                        ),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                cat_features,
            ),
        ]
    )

    pipe = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "feature_selection",
                SelectFromModel(
                    estimator=RandomForestClassifier(n_estimators=200, random_state=42)
                ),
            ),
            ("classifier", MLPClassifier(random_state=42)),
        ]
    )

    param_grid = {
        "feature_selection__threshold": [0, 0.0001],
        "feature_selection__estimator__max_features": [84],
        "preprocessor__num__imputer__n_neighbors": [5],
        "classifier__hidden_layer_sizes": [(50,), (100,)],
        "classifier__alpha": np.logspace(-5, -1, 5),
        # "classifier__learning_rate": ["constant", "adaptive"], à utiliser si le solver est sgd
        # "classifier__max_iter": [200, 400],
        "classifier__early_stopping": [True],
        "classifier__validation_fraction": [0.1],
        # "classifier__n_iter_no_change": [10],
        # "classifier__warm_start": [False],
        "classifier__solver": ["adam"],
        "classifier__activation": ["relu"],
        # "classifier__batch_size": [200, 400],
        # "classifier__learning_rate_init": [0.001], à utiliser si le solver est sgd ou adam
        # "classifier__power_t": [0.5], à utiliser si le solver est sgd
        # "classifier__momentum": [0.9], à utiliser si le solver est sgd
        # "classifier__nesterovs_momentum": [True], à utiliser si le solver est
        # "classifier__shuffle": [True], à utiliser si le solver est sgd ou adam
    }

    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, n_jobs=-2, pre_dispatch="2*n_jobs"
    )
    with parallel_backend("loky"):
        grid_search.fit(X_train, y_train)

    score_test = grid_search.score(X_test, y_test)
    return grid_search.best_estimator_, score_test
