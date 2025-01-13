"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour le modèle SVM
"""

from sklearn.ensemble import GradientBoostingClassifier
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


def _pipeline_boosting(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
) -> tuple[ColumnTransformer, Pipeline]:
    """
    Cette fonction créer un pipeline dans le but d'optimiser les hyperparamètres du modèle boosting
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
                        ("imputer", KNNImputer()),
                        ("scaler", StandardScaler()),
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
                            "imputer",
                            # SimpleImputer(strategy='most_frequent'),
                            SimpleImputer(
                                strategy="constant", fill_value="non-renseigné"
                            ),
                        ),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
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
                "feature_selection",
                SelectFromModel(
                    estimator=RandomForestClassifier(n_estimators=400, random_state=42)
                ),
            ),
            ("classifier", GradientBoostingClassifier()),
        ]
    )

    param_grid = {
        "feature_selection__threshold": [0.001],
        "preprocessor__num__imputer__n_neighbors": [700],
        "classifier__n_estimators": [300],
        "classifier__learning_rate": [0.1],
        "classifier__subsample": [1],
        "classifier__max_depth": [2],
        "classifier__min_impurity_decrease": [0.7],
    }

    grid_search = GridSearchCV(
        pipe, param_grid, cv=5, n_jobs=-1, pre_dispatch="2*n_jobs"
    )
    with parallel_backend("loky"):
        grid_search.fit(
            X_train,
            y_train[variable_a_predire],
            classifier__sample_weight=y_train[variable_de_poids],
        )

    return dict(
        nom="GradientBoostingClassifier",
        modele=grid_search.best_estimator_,
        score_entrainement=grid_search.best_score_,
    )
