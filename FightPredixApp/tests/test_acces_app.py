from streamlit.testing.v1 import AppTest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_app():
    """
    Test de l'accès à l'application
    """
    app = AppTest.from_file("FightPredixApp/app.py", default_timeout=15)

    app.run()  # Lancement de l'application

    app.button[1].click().run()  # Bouton apge Combattants

    app.selectbox[0].select("Heavyweight").run()  # Selection de la catégorie de poids

    app.selectbox[1].select("JON JONES").run()  # Selection du combattant 1

    app.selectbox[2].select("CIRYL GANE").run()  # Selection du combattant 2

    app.table[0].run()  # le tableau de données des combattants

    app.button[3].click().run()  # bouton de prédiction

    app.button[
        2
    ].click().run()  # bouton page Prédiction, en cliquant dessus cela lance aussi le test pour la verification de la presence du modele dans le dossier modele

    assert not app.exception
