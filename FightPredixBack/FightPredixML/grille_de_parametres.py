"""Description:

Ce fichier contient les grilles de paramètres pour les modèles de machine learning : boosting, random forest, regression logistique, neural network et svm.
"""

import numpy as np

parametres_boosting = {
    "preprocessor__num__knn_imputer__n_neighbors": [100, 400, 800],
    "preprocessor__num__Suppress_low_var__threshold": [0.9 * (1 - 0.9)],
    "feature_selection_random_forest__threshold": [0, 0.001, 0.05],
    "feature_selection_random_forest__estimator__n_estimators": [400],
    "feature_selection_random_forest__estimator__max_features": [84],
    "boosting__n_estimators": [100, 250, 500, 1000],
    "boosting__learning_rate": [0.001, 0.01, 0.1],
    "boosting__max_depth": [1, 2, 5],
}

parametres_random_forest = {
    "preprocessor__num__knn_imputer__n_neighbors": [100, 400, 800],
    "preprocessor__num__Suppress_low_var__threshold": [0.9 * (1 - 0.9)],
    "feature_selection_random_forest__threshold": [0, 0.001, 0.05],
    "feature_selection_random_forest__estimator__n_estimators": [400],
    "feature_selection_random_forest__estimator__max_features": [84],
    "random_forest__criterion": ["entropy"],
    "random_forest__n_estimators": [200, 500, 800],
    # "random_forest__min_samples_split": [2],
    "random_forest__max_depth": [10, 15, 25, 30],
    # "random_forest__min_samples_leaf": [1],
}

parametres_regression_logistique = {
    "preprocessor__num__Suppress_low_var__threshold": [0.9 * (1 - 0.9)],
    "feature_selection_random_forest__threshold": [0, 0.001, 0.05],
    "feature_selection_random_forest__estimator__n_estimators": [400],
    "feature_selection_random_forest__estimator__max_features": [84],
    "preprocessor__num__knn_imputer__n_neighbors": [400],
    "regression_logistique__penalty": ["l1"],
}

parametres_neural_network = {
    "feature_selection_random_forest__threshold": [0, 0.0001, 0.05],
    "feature_selection_random_forest__estimator__max_features": [84],
    "feature_selection_random_forest__estimator__n_estimators": [400],
    "preprocessor__num__knn_imputer__n_neighbors": [100, 400, 800],
    "preprocessor__num__Suppress_low_var__threshold": [0.9 * (1 - 0.9)],
    "neural_network__hidden_layer_sizes": [(50,), (50, 2), (80,), (150,)],
    "neural_network__alpha": np.logspace(-5, np.log10(1 / 2), 20),
    "neural_network__early_stopping": [True],
    "neural_network__solver": ["adam"],
    "neural_network__activation": ["relu"],
}

parametres_svm = {
    "feature_selection_random_forest__threshold": [0, 0.0001, 0.05],
    "feature_selection_random_forest__estimator__n_estimators": [400],
    "feature_selection_random_forest__estimator__max_features": [84],
    "preprocessor__num__knn_imputer__n_neighbors": [100, 400, 800],
    "preprocessor__num__Suppress_low_var__threshold": [0.9 * (1 - 0.9)],
    "svm__C": np.logspace(-3, 3, 20),
    "svm__gamma": np.logspace(-5, np.log10(1 / 2), 20),
}
