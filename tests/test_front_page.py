"""Teste les fonctions de lib_front_page.py"""

import pytest


@pytest.fixture
def webdriver():
    from selenium import webdriver

    driver = webdriver.Chrome()

    def finalizer():
        """
        teardown : ferme le navigateur à la fin du test afin de ne laisser aucune instance de navigateur ouverte
        """

        driver.close()
        driver.quit()

    return driver


@pytest.fixture
def url():
    return "https://www.ufc.com/athletes/all"


def test_requete_page_souhaitee(webdriver, url):
    """
    On vérifie que la page souhaitée a bien été atteinte
    """

    webdriver.get(url)
    assert webdriver.current_url == url
