"""Description

Contient le pipeline et l'optimisation des hyperparamètres pour le modèle SVM
"""

from typing import Union
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
from datetime import datetime
from FightPredixBack.outils import configure_logger

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_optimisation_random_forest")


def _pipeline_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    variables_numeriques: list[str],
    variables_categorielles: list[str],
    variable_a_predire: str,
    variable_de_poids: str,
    cv: int,
    param_grid: dict,
    n_jobs: int,
    random_state: int,
    verbose: int,
) -> dict[str, Union[str, Pipeline, float]]:
    """
    Cette fonction crée un pipeline dans le but d'optimiser les hyperparamètres du modèle Random Forest
    """

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    [
                        (
                            "Suppress_low_var",
                            VarianceThreshold(),
                        ),
                        ("knn_imputer", KNNImputer()),
                        ("standard_scaler", StandardScaler()),
                        ("PCA", PCA(random_state=random_state)),
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
                    estimator=RandomForestClassifier(
                        random_state=random_state, verbose=verbose
                    )
                ),
            ),
            (
                "random_forest",
                RandomForestClassifier(verbose=verbose, random_state=random_state),
            ),
        ]
    )

    grid_search = GridSearchCV(
        pipe, param_grid, cv=cv, n_jobs=n_jobs, pre_dispatch="2*n_jobs"
    )
    with parallel_backend("loky"):
        grid_search.fit(
            X_train,
            y_train[variable_a_predire],
            random_forest__sample_weight=y_train[variable_de_poids],
        )
    logger.info(
        f"Meilleurs hyperparamètres pour le modèle Random Forest : {grid_search.best_params_}"
    )
    logger.info(
        f"Meilleurs scores d'entrainement pour le modèle Random Forest : {grid_search.best_score_}"
    )
    return dict(
        nom="Random Forest Classifier",
        modele=grid_search.best_estimator_,
        score_entrainement=grid_search.best_score_,
    )
