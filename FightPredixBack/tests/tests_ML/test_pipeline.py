"""Teste les pipelines de préparation des données pour les modèles de Machine Learning"""

from FightPredixBack.FightPredixML.optimiser_svm import _pipeline_svm
from FightPredixBack.FightPredixML.opitmiser_random_forest import (
    _pipeline_random_forest,
)
from FightPredixBack.FightPredixML.optimiser_neural_network import (
    _pipeline_neural_network,
)
from FightPredixBack.FightPredixML.opitmiser_regression_logistique import (
    _pipeline_regression_logistique,
)
from FightPredixBack.FightPredixML.opitmiser_boosting import _pipeline_boosting
import unittest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


class TestPipelineSVM(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = pd.DataFrame(
            {
                "num_feature1": np.random.rand(100),
                "num_feature2": np.random.rand(100),
                "cat_feature1": np.random.choice(["A", "B", "C"], 100),
                "cat_feature2": np.random.choice(["X", "Y", "Z"], 100),
            }
        )
        self.y = pd.DataFrame(
            {"target": np.random.choice([0, 1], 100), "weights": np.random.rand(100)}
        )

        self.variables_numeriques = ["num_feature1", "num_feature2"]
        self.variables_categorielles = ["cat_feature1", "cat_feature2"]
        self.variable_a_predire = "target"
        self.variable_de_poids = "weights"
        self.cv = 5
        self.param_grid = {"svm__C": [0.1, 1, 10], "svm__gamma": [0.01, 0.1, 1]}
        self.n_jobs = -2
        self.random_state = 42
        self.verbose = 0

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.3, random_state=self.random_state
        )

    def test_pipeline_svm(self):
        result = _pipeline_svm(
            self.X_train,
            self.y_train,
            self.variables_numeriques,
            self.variables_categorielles,
            self.variable_a_predire,
            self.variable_de_poids,
            self.cv,
            self.param_grid,
            self.n_jobs,
            self.random_state,
            self.verbose,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("nom", result)
        self.assertIn("modele", result)
        self.assertIn("score_entrainement", result)
        self.assertEqual(result["nom"], "SVM Classifier")
        self.assertIsInstance(result["modele"], Pipeline)
        self.assertIsInstance(result["score_entrainement"], float)


class TestPipelineRandomForest(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = pd.DataFrame(
            {
                "num_feature1": np.random.rand(100),
                "num_feature2": np.random.rand(100),
                "cat_feature1": np.random.choice(["A", "B", "C"], 100),
                "cat_feature2": np.random.choice(["X", "Y", "Z"], 100),
            }
        )
        self.y = pd.DataFrame(
            {"target": np.random.choice([0, 1], 100), "weights": np.random.rand(100)}
        )

        self.variables_numeriques = ["num_feature1", "num_feature2"]
        self.variables_categorielles = ["cat_feature1", "cat_feature2"]
        self.variable_a_predire = "target"
        self.variable_de_poids = "weights"
        self.cv = 5
        self.param_grid = {
            "random_forest__n_estimators": [100, 200, 300],
            "random_forest__max_depth": [5, 10, 15],
        }
        self.n_jobs = -2
        self.random_state = 42
        self.verbose = 0

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )

    def test_pipeline_random_forest(self):
        result = _pipeline_random_forest(
            self.X_train,
            self.y_train,
            self.variables_numeriques,
            self.variables_categorielles,
            self.variable_a_predire,
            self.variable_de_poids,
            self.cv,
            self.param_grid,
            self.n_jobs,
            self.random_state,
            self.verbose,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("nom", result)
        self.assertIn("modele", result)
        self.assertIn("score_entrainement", result)
        self.assertEqual(result["nom"], "Random Forest Classifier")
        self.assertIsInstance(result["modele"], Pipeline)
        self.assertIsInstance(result["score_entrainement"], float)


class TestPipelineNeuralNetwork(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = pd.DataFrame(
            {
                "num_feature1": np.random.rand(100),
                "num_feature2": np.random.rand(100),
                "cat_feature1": np.random.choice(["A", "B", "C"], 100),
                "cat_feature2": np.random.choice(["X", "Y", "Z"], 100),
            }
        )
        self.y = pd.DataFrame(
            {"target": np.random.choice([0, 1], 100), "weights": np.random.rand(100)}
        )

        self.variables_numeriques = ["num_feature1", "num_feature2"]
        self.variables_categorielles = ["cat_feature1", "cat_feature2"]
        self.variable_a_predire = "target"
        self.variable_de_poids = "weights"
        self.cv = 3
        self.param_grid = {
            "neural_network__hidden_layer_sizes": [(100,), (200,), (300,)],
            "neural_network__alpha": [0.0001, 0.001, 0.01],
        }
        self.n_jobs = -2
        self.random_state = 42
        self.verbose = 0

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )

    def test_pipeline_neural_network(self):
        result = _pipeline_neural_network(
            self.X_train,
            self.y_train,
            self.variables_numeriques,
            self.variables_categorielles,
            self.variable_a_predire,
            self.variable_de_poids,
            self.cv,
            self.param_grid,
            self.n_jobs,
            self.random_state,
            self.verbose,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("nom", result)
        self.assertIn("modele", result)
        self.assertIn("score_entrainement", result)
        self.assertEqual(result["nom"], "neural_network Classifier")
        self.assertIsInstance(result["modele"], Pipeline)
        self.assertIsInstance(result["score_entrainement"], float)


class TestPipelineRegressionLogistique(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = pd.DataFrame(
            {
                "num_feature1": np.random.rand(100),
                "num_feature2": np.random.rand(100),
                "cat_feature1": np.random.choice(["A", "B", "C"], 100),
                "cat_feature2": np.random.choice(["X", "Y", "Z"], 100),
            }
        )
        self.y = pd.DataFrame(
            {"target": np.random.choice([0, 1], 100), "weights": np.random.rand(100)}
        )

        self.variables_numeriques = ["num_feature1", "num_feature2"]
        self.variables_categorielles = ["cat_feature1", "cat_feature2"]
        self.variable_a_predire = "target"
        self.variable_de_poids = "weights"
        self.cv = 3
        self.param_grid = {
            "regression_logistique__C": [0.1, 1, 10],
            "regression_logistique__penalty": ["l2"],
        }
        self.n_jobs = -2
        self.random_state = 42
        self.verbose = 0

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )

    def test_pipeline_regression_logistique(self):
        result = _pipeline_regression_logistique(
            self.X_train,
            self.y_train,
            self.variables_numeriques,
            self.variables_categorielles,
            self.variable_a_predire,
            self.variable_de_poids,
            self.cv,
            self.param_grid,
            self.n_jobs,
            self.random_state,
            self.verbose,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("nom", result)
        self.assertIn("modele", result)
        self.assertIn("score_entrainement", result)
        self.assertEqual(result["nom"], "Régression logistique")
        self.assertIsInstance(result["modele"], Pipeline)
        self.assertIsInstance(result["score_entrainement"], float)


class TestPipelineBoosting(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)
        self.X = pd.DataFrame(
            {
                "num_feature1": np.random.rand(100),
                "num_feature2": np.random.rand(100),
                "cat_feature1": np.random.choice(["A", "B", "C"], 100),
                "cat_feature2": np.random.choice(["X", "Y", "Z"], 100),
            }
        )
        self.y = pd.DataFrame(
            {"target": np.random.choice([0, 1], 100), "weights": np.random.rand(100)}
        )

        self.variables_numeriques = ["num_feature1", "num_feature2"]
        self.variables_categorielles = ["cat_feature1", "cat_feature2"]
        self.variable_a_predire = "target"
        self.variable_de_poids = "weights"
        self.cv = 3
        self.param_grid = {
            "boosting__n_estimators": [100, 200, 300],
            "boosting__learning_rate": [0.01, 0.1, 1],
        }
        self.n_jobs = -2
        self.random_state = 42
        self.verbose = 0

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )

    def test_pipeline_boosting(self):
        result = _pipeline_boosting(
            self.X_train,
            self.y_train,
            self.variables_numeriques,
            self.variables_categorielles,
            self.variable_a_predire,
            self.variable_de_poids,
            self.cv,
            self.param_grid,
            self.n_jobs,
            self.random_state,
            self.verbose,
        )

        self.assertIsInstance(result, dict)
        self.assertIn("nom", result)
        self.assertIn("modele", result)
        self.assertIn("score_entrainement", result)
        self.assertEqual(result["nom"], "GradientBoostingClassifier")
        self.assertIsInstance(result["modele"], Pipeline)
        self.assertIsInstance(result["score_entrainement"], float)


if __name__ == "__main__":
    unittest.main()
