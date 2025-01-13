"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour le modèle SVM
"""

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_selection import VarianceThreshold, SelectFromModel
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
from joblib import parallel_backend
from sklearn.decomposition import PCA


def _pipeline_naive_bayes(
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
            ("classifier", SVC(class_weight="balanced", random_state=42)),
        ]
    )

    param_grid = {
        "feature_selection__threshold": [0, 0.0001],
        "feature_selection__estimator__max_features": [42, 84],
        "preprocessor__num__imputer__n_neighbors": [5, 500],
        "classifier__C": np.logspace(-4, 4, 10),  # *n_sample
        "classifier__gamma": np.logspace(-5, np.log10(1 / 2), 10),  # 1/n_features
    }

    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, n_jobs=-1, pre_dispatch="2*n_jobs"
    )
    with parallel_backend("loky"):
        grid_search.fit(X_train, y_train)

    return dict(
        nom="Naive Bayes Classifier",
        modele=grid_search.best_estimator_,
        score_entrainement=grid_search.best_score_,
    )
