"""Description

Optimisation des hyperparamètres du modèle SVM
"""

from .lib_nettoyage_avant_preprocess import _main_nettoyage, _liste_features
from .lib_process_avant_model import _main_process_avant_model
from .lib_neural_network import _pipeline
from rich.console import Console
import joblib

if __name__ == "__main__":
    console = Console()
    console.print("Nettoyage des données en cours...")
    Data = _main_nettoyage()
    num_features, cat_features, poids = _liste_features()
    X, y, poids_ml = _main_process_avant_model(Data)
    console.print("Entrainement du modèle en cours...")
    best_estimator, score_test = _pipeline(X, y, num_features, cat_features)
    console.print(f"Meilleur estimateur: {best_estimator}")
    console.print(f"Score test: {score_test}")
    # Sauvegarde du modèle
    joblib.dump(best_estimator, "SVM_model.pkl")
