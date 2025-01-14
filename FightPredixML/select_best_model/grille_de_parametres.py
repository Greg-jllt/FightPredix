"""Description:

Ce fichier contient les grilles de paramètres pour les modèles de machine learning : boosting, random forest, regression logistique, neural network et svm.
"""

parametres_boosting = {
    "preprocessor__num__knn_imputer__n_neighbors": [700],
    "feature_selection_random_forest__threshold": [0.001],
    "boosting__n_estimators": [300],
    "boosting__learning_rate": [0.1],
    "boosting__subsample": [1],
    "boosting__max_depth": [2],
    "boosting__min_impurity_decrease": [0.7],
}

parametres_random_forest = {
    "feature_selection_random_forest__threshold": [0.001],
    "preprocessor__num__knn_imputer__n_neighbors": [700],
    "random_forest__criterion": ["entropy"],
    "random_forest__n_estimators": [400],
    "random_forest__min_samples_split": [2],
    "random_forest__max_depth": [25],
    "random_forest__min_samples_leaf": [1],
}

parametres_regression_logistique = {
    "feature_selection_random_forest__threshold": [0.001],
    "preprocessor__num__knn_imputer__n_neighbors": [700],
    "regression_logistique__penalty": ["l1", "l2"],
    "regression_logistique__C": [0.5],
    "regression_logistique__tol": [1e-2],
    "regression_logistique__solver": ["liblinear"],
}

parametres_neural_network = {
    "feature_selection_random_forest__threshold": [0.0001],
    "feature_selection_random_forest__estimator__max_features": [84],
    "feature_selection_random_forest__estimator__n_estimators": [200],
    "preprocessor__num__knn_imputer__n_neighbors": [5],
    "neural_network__hidden_layer_sizes": [(50,)],
    "neural_network__alpha": [5],
    "neural_network__early_stopping": [True],
    "neural_network__validation_fraction": [0.1],
    "neural_network__solver": ["adam"],
    "neural_network__activation": ["relu"],
}

parametres_svm = {
    "feature_selection_random_forest__threshold": [0.0001],
    "feature_selection_random_forest__estimator__n_estimators": [250],
    "feature_selection_random_forest__estimator__max_features": [84],
    "preprocessor__num__knn_imputer__n_neighbors": [500],
    "svm__C": [100],
    "svm__gamma": [0.001],
}
