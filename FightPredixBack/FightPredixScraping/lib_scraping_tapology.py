"""
Librairie pour recolter les informations des combattants de l'UFC sur https://www.tapology.com

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import polars as pl
from collections import defaultdict
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import subprocess
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from FightPredixBack.outils import configure_logger

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_scraping_tapology")


def _connect_vpn():
    """
    Connexion à un VPN
    """

    try:
        subprocess.run(
            "nordvpn --connect -g France",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Connected to NordVPN")
        time.sleep(10)
    except subprocess.CalledProcessError as e:
        logger.error(f"Problème à la déconnection du vpn:\n{e}")


def _disconnect_vpn():
    """
    Déconnection du VPN actuel
    """

    try:
        subprocess.run(
            "nordvpn --disconnect -g France",
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Disconnected from NordVPN")
        time.sleep(10)
    except subprocess.CalledProcessError as e:
        logger.error(f"Problème à la connection du vpn:\n {e}")


def _recherche_nom(
    nom_ufc: str,
    driver: webdriver.Chrome,
    chrome_options: webdriver.ChromeOptions,
    url_tapology: str,
) -> webdriver.Chrome:
    """
    Fonction qui recherche un combattant sur tapology
    """

    if nom_ufc in change_name["mauvais_nom"]:
        nom = change_name["bon_noms"][change_name["mauvais_nom"].index(nom_ufc)]
    else:
        nom = nom_ufc
    while True:
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="siteSearch"]'))
            )
            search_box.send_keys(nom)
            search_box.send_keys(Keys.RETURN)
            break
        except WebDriverException as e:
            logger.warning(f"Erreur de connexion lors de la recherche de {nom}: {e}")
            driver = _restart_with_new_vpn(
                driver=driver, url=url_tapology, options=chrome_options
            )
    return driver


def _explorer_combattant(
    driver: webdriver.Chrome,
    url: str,
    chrome_options: webdriver.ChromeOptions,
    nom: str,
) -> tuple[webdriver.Chrome, bool]:
    """
    Fonction qui recherche le premier combattant trouvé
    """

    current_url = driver.current_url
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            elements = soup.find_all("td", class_="altA")
            if not elements:
                raise IndexError("Combattant non trouvé")
            lien = url + elements[0].find("a")["href"]
            driver.get(lien)
            return driver, True
        except (IndexError, AttributeError) as e:
            logger.warning(f"Erreur lors de l'exploration du combattant: {e}")
            return driver, False
        except WebDriverException as e:
            logger.warning(f"Erreur de connexion lors de l'exploration de {nom}: {e}")
            driver = _restart_with_new_vpn(
                driver=driver, url=current_url, options=chrome_options
            )


def _scraper_combattant(
    driver: webdriver.Chrome, nom_ufc: str, chrome_options: webdriver.ChromeOptions
) -> tuple[defaultdict, webdriver.Chrome]:
    """
    Fonction qui recolte les informations d'un combattant sur tapology
    """

    current_url = driver.current_url
    if nom_ufc in change_name["mauvais_nom"]:
        nom = change_name["bon_noms"][change_name["mauvais_nom"].index(nom_ufc)]
    else:
        nom = nom_ufc
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            dictio: defaultdict = defaultdict()
            tableau = soup.find("div", attrs={"id": "standardDetails"})
            ligne = tableau.find_all("div")  # type: ignore
            dictio["NAME"] = nom_ufc
            logger.info(f"Scraping de {dictio['NAME']}")
            for cellule in ligne:
                var = cellule.find("strong")
                value = cellule.find("span")
                if var and value:
                    dictio[var.text.strip() + "tapology"] = value.text.strip()
            return dictio, driver
        except Exception as e:
            logger.warning(f"Erreur lors du scraping de {nom}: {e}")
            driver = _restart_with_new_vpn(
                driver=driver, url=current_url, options=chrome_options
            )


def _procedure_de_scraping(
    driver: webdriver.Chrome,
    url: str,
    nom: str,
    chrome_options: webdriver.ChromeOptions,
) -> tuple[defaultdict | None, webdriver.Chrome]:
    """
    Fonction contenant la procédure de scraping : recherche du combattant, accés à sa page puis scraping de ses caractéristiques
    """

    driver.implicitly_wait(30)
    try:
        driver = _recherche_nom(nom, driver, chrome_options, url)
        time.sleep(2)
        driver.implicitly_wait(20)
        driver, combattant_trouvee = _explorer_combattant(
            driver, url, chrome_options, nom
        )
        driver.implicitly_wait(10)
        if not combattant_trouvee:
            raise Exception("Combattant non trouvé")
        else:
            dictio, driver = _scraper_combattant(
                driver, nom_ufc=nom, chrome_options=chrome_options
            )
    except Exception as e:
        logger.warning(f"Erreur lors de la procédure de scraping pour {nom}: {e}\n")
        dictio = None
    return dictio, driver


def _restart_with_new_vpn(
    driver: webdriver.Chrome, url: str, options: webdriver.ChromeOptions
):
    """
    Fonction qui réinitialise un driver avec un nouveau vpn en cas d'échec
    """

    driver.quit()
    _disconnect_vpn()
    _connect_vpn()
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def _starting_driver() -> tuple[webdriver.Chrome, str, webdriver.ChromeOptions]:
    """
    Initialisation du driver
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    )
    chrome_options.add_argument("--headless")
    url_tapology = "https://www.tapology.com"
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url_tapology)
    return driver, url_tapology, chrome_options


def _update_and_log_fighters(
    liste_combattant: list[str],
) -> tuple[pl.DataFrame, list[str], set[str]]:
    """
    Fonction qui met à jour les données des combattants déjà scrapés et les retire de la liste des combattants à scraper
    """

    try:
        with open(
            "FightPredixBack/FightPredixScraping/temp_data/actual_combattant_tapology.json"
        ) as f:
            data_tapology = json.load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Fichier introuvable:\n{e}")

    data_tapology = pl.DataFrame(data_tapology).unique()
    listes_noms_tapology = [
        nom.strip().lower() for nom in data_tapology["NAME"].unique().to_list()
    ]
    liste_combattant_traites = set()
    for nom in listes_noms_tapology:
        if nom in liste_combattant:
            liste_combattant.remove(nom)
            liste_combattant_traites.add(nom)

    return data_tapology, liste_combattant, liste_combattant_traites


def _initialisation_des_donnees_a_scraper(
    recuperer_ancien_scraping: bool,
) -> tuple[pl.DataFrame, pl.DataFrame, list[str], set[str]]:
    """
    Si le script a planté, on reprend le scraping seulement pour les combattants non-scrapés (à placer en option)
    """

    try:
        data_ufc = pl.read_json(
            "FightPredixBack/FightPredixScraping/temp_data/Data_ufc_fighters.json"
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Fichier introuvable:\n{e}")

    liste_combattant = [nom.strip().lower() for nom in data_ufc["NAME"].to_list()]
    liste_combattant_traites: set[str] = set()

    if recuperer_ancien_scraping:
        data_tapology, liste_combattant, liste_combattant_traites = (
            _update_and_log_fighters(liste_combattant)
        )

        return data_ufc, data_tapology, liste_combattant, liste_combattant_traites
    else:
        return data_ufc, pl.DataFrame(), liste_combattant, liste_combattant_traites


def _fusionner_tapologies(combattant: defaultdict):
    """
    Fonction qui fusionne les données de tapology
    """

    try:
        with open(
            "FightPredixBack/FightPredixScraping/temp_data/actual_combattant_tapology.json"
        ) as f:
            data = json.load(f)
        data.append(combattant)
        with open(
            "FightPredixBack/FightPredixScraping/temp_data/actual_combattant_tapology.json",
            "w",
        ) as f:
            json.dump(data, f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Fichier introuvable:\n{e}")


change_name = dict(
    mauvais_nom=[
        "alberto cerro leon",
        "alex steibling",
        "alexander morgan",
        "anthony fryklund",
        "antonio silva",
        "belal muhammad",
        "billy ray goff",
        "brandon lewis",
        "chanmi jeon",
        "chris ligouri",
        "christophe leininger",
        "christophe midoux",
        "cj vergara",
        "cristina stanciu",
        "daniel bobish",
        "dmitrei stepanov",
        "dmitrii smoliakov",
        "dooho choi",
        "elias urbina",
        "emmanuel yarbrough",
        "erick montano",
        "felix lee mitchell",
        "hanseul kim",
        "hyunsung park",
        "jack nilsson",
        "jeongyeong lee",
        "joe moriera",
        "john campetella",
        "josh raferty",
        "junyoung hong",
        "keichiro yamamiya",
        "kj noons",
        "loma lookboonmee",
        "maia stevenson",
        "maiara amajanas dos santos",
        "marcello mello",
        "marcello aguiar",
        "marcus da silviera",
        "minwoo kim",
        "nariman abbassov",
        "orlando welt",
        "reza nazri",
        "riley dutro",
        "roman salazar",
        "ryan mcgilivray",
        "saimon oliveira",
        "scott fielder",
        "sean daughtery",
        "seokhyeon ko",
        "seongchan hong",
        "shawn jordan",
        "sinae kikuta",
        "sione latu",
        "suyoung you",
        "tedd williams",
        "tony peterra",
        "wonbin ki",
        "yedam seo",
        "zach light",
        "cory sandhagen",
        "elias theodorou",
        "vanessa melo",
        "michael lombardo",
        "seungguk choi",
        "donghun choi",
        "richard crunkilton jr.",
        "seungwoo choi",
        "kyeongpyo kim",
        "jake o'brien",
        "junyong park",
        "henrique da silva lopes",
        "justin jones",
        "norma dumont",
        "kazushi sakuraba",
        "allen berube",
        "donavan beard",
        "duane cason",
        "marcos conrado junior",
        "oleksandr doskalchuk",
        "aleksei kunchenko",
        "jason macdonald",
        "nazareno malegarie",
        "kenneth cross",
        "giga chikadze",
        "diego henrique da silva",
        "dayana da silva santos",
        "leonardo augusto leleco",
        "mark david robinson",
        "steve regman",
        "nair nelikyan",
        "tj o'brien",
        "geza kahlman jr",
        "angel de anda",
    ],
    bon_noms=[
        "alberto cerra leon",
        "alex stiebling",
        "alex morgan",
        "tony fryklund",
        "bigfoot",
        "remember the name",
        "billy goff",
        "let's go b",
        "chan mi jeon",
        "chris liguori",
        "cristophe leninger",
        "kristof midoux",
        "CJ Vergara",
        "barbie cr",
        "dan bobish",
        "dmitriy stepanov",
        "dmitry smoliakov",
        "doo ho choi",
        "Elias Urbina",
        "emmanuel yarborough",
        "erick mont",
        "felix mitchell",
        "han seul kim",
        "hyun sung park",
        "jack nilson",
        "jeong yeong lee",
        "joe moreira",
        "john campatella",
        "josh rafferty",
        "jun young hong",
        "keiichiro yamamiya",
        "King Karl k",
        "Loma Lookboonmee",
        "Maia Kahaunaele",
        "Maiara Amanajás",
        "marcelo mello",
        "marcelo aguiar",
        "marcus silveira",
        "min woo kim",
        "nariman abbasov",
        "orlando wiet",
        "reza nasri",
        "rilley dutro",
        "El Gallito Rom",
        "ryan mcgillivray",
        "Saimon Oliveira",
        "scott fiedler",
        "sean daugherty",
        "seok hyun ko",
        "seong chan hong",
        "The Savage Shawn",
        "sanae kikuta",
        "zzzzzzzzzzzzzzzzzz",
        "su young you",
        "Tedd Williams",
        "tony petarra",
        "won bin ki",
        "ye dam seo",
        "The lisbon outlaw Zach",
        "Sandman Cory",
        "The Spartan Elias",
        "Miss Simpatia vanessa",
        "Anvil Michael",
        "seung guk choi",
        "dong hun choi",
        "richard crunkilton",
        "seung woo choi",
        "kyeong pyo kim",
        "Jake O'Brien",
        "jun yong park",
        "Henrique Silva",
        "Lazy bones Justin Jones",
        'Norma "The Immortal" Dumont',
        '"The Gracie Hunter" Kazushi Sakuraba',
        "allen berubie",
        "donovan beard",
        "dwayne cason",
        "marcos conrado jr",
        "aleksander doskalchuk",
        "alexey kunchenko",
        "the athlete jason",
        "El tigre nazareno",
        "the boss kenneth",
        "Ninja giga",
        "gaucho diego henrique",
        "dayana silva",
        "leonardo guimaraes",
        "mark robinson",
        "stephen regman",
        "nair melikyan",
        "the spider o'b",
        "Geza Kalman",
        "angel deanda",
    ],
)


def _main_scraping_tapology():
    driver, url_tapology, chrome_options = _starting_driver()
    recuperer_ancien_scraping = False

    _, _, liste_combattant, liste_combattant_traites = (
        _initialisation_des_donnees_a_scraper(
            recuperer_ancien_scraping=recuperer_ancien_scraping
        )
    )

    liste_combattant_scrapes = list()
    liste_combattant_non_trouve = set()
    iteration = 0
    while True:
        iteration += 1
        if iteration > 3:
            break
        compteur = 0
        logger.info(
            f"-------------------------------------------------------------\nItération n°{iteration}\n-----------------------------------------------------------------------------------------------"
        )
        logger.info(
            f"Nombre de combattants restants à scraper: {len(liste_combattant)}"
        )
        try:
            for nom in liste_combattant:
                if nom in liste_combattant_traites:
                    continue
                compteur += 1
                logger.info(f"Recherche n°{compteur}, Recherche du combattant: {nom}")

                dictio, driver = _procedure_de_scraping(
                    driver=driver,
                    url=url_tapology,
                    nom=nom,
                    chrome_options=chrome_options,
                )
                if dictio:
                    driver.implicitly_wait(10)
                    logger.info(f"Combattant trouvé et ajouté: {nom}\n")
                    liste_combattant_traites.add(nom)

                    if recuperer_ancien_scraping:
                        _fusionner_tapologies(dictio)
                    else:
                        liste_combattant_scrapes.append(dictio)
                        with open(
                            "FightPredixBack/FightPredixScraping/temp_data/final_tapology.json",
                            "w",
                        ) as f:
                            json.dump(liste_combattant_scrapes, f)
                else:
                    liste_combattant_non_trouve.add(nom)
                    continue
        except Exception as e:
            logger.warning(f"Erreur lors du scraping: {e}")
            if not recuperer_ancien_scraping:
                with open(
                    "FightPredixBack/FightPredixScraping/temp_data/actuel_combattant_tapology.json",
                    "w",
                ) as f:
                    json.dump(liste_combattant_scrapes, f)

    driver.quit()
    for nom in liste_combattant:
        if nom not in liste_combattant_traites:
            liste_combattant_non_trouve.add(nom)
    logger.info(
        f"Scraping terminé. Les combattants suivants n'ont pas été trouvés: {liste_combattant_non_trouve}"
    )
