"""Description:

Ce fichier contient les fonctions fixtures qui seront utilisées dans les tests unitaires.
"""

import os
import sys
import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def driver():
    """
    Fixture initialisant le webdriver Chrome
    """
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
    """
    Fixture retournant l'url de la page principale
    """

    return "https://www.ufc.com/athletes/all"


@pytest.fixture
def url_combattant():
    """
    Fixture retournant l'url d'un combattant
    """

    return "https://www.ufc.com/athlete/danny-abbadi"


@pytest.fixture
def soup_combattant(driver, url_combattant):
    """
    Fixture retournant l'objet BeautifulSoup de la page d'un combattant
    """

    driver.get(url_combattant)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


@pytest.fixture
def url_anciens_champions():
    """
    Fixture retournant l'url de la page des anciens champions
    """

    return "https://fr.wikipedia.org/wiki/Liste_des_champions_de_l'UFC"


@pytest.fixture
def soup_anciens_champions(driver, url_anciens_champions):
    """
    Fixture retournant l'objet BeautifulSoup de la page des anciens champions
    """

    driver.get(url_anciens_champions)
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    return soup
