"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour le modèle SVM
"""

from typing import Union
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_selection import VarianceThreshold, SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from joblib import parallel_backend
from sklearn.decomposition import PCA


def _pipeline_svm(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
    param_grid: dict,
) -> dict[str, Union[str, Pipeline, float]]:
    """
    Cette fonction créer un pipeline dans le but d'optimiser les hyperparamètres du modèle SVM
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
                SelectFromModel(estimator=RandomForestClassifier(random_state=42)),
            ),
            ("svm", SVC(class_weight="balanced", random_state=42)),
        ]
    )

    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, n_jobs=-1, pre_dispatch="2*n_jobs"
    )

    with parallel_backend("loky"):
        grid_search.fit(
            X_train,
            y_train[variable_a_predire],
            svm__sample_weight=y_train[variable_de_poids],
        )

    return dict(
        nom="SVM Classifier",
        modele=grid_search.best_estimator_,
        score_entrainement=grid_search.best_score_,
    )
