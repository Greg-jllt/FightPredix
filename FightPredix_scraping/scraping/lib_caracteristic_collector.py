"""
Librairie qui permet de collecter les caractéristiques des combattants de l'UFC

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from collections import defaultdict
from selenium import webdriver
from rich.console import Console
from selenium.webdriver.common.by import By

import re


def _infos_principal_combattant(
    driver , dictio: defaultdict
) -> bool:
    """
    Fonction qui extrait les informations principales d'un combattant
    """

    nickname_elements = driver.find_elements(By.CSS_SELECTOR, "p.hero-profile__nickname")
    dictio["NICKNAME"] = nickname_elements[0].text.strip() if nickname_elements else None


    elements = driver.find_elements(By.CSS_SELECTOR, ".hero-profile__division-title, .hero-profile__division-body")

    if elements:
        texts = [el.text.strip() for el in elements]

        for text in texts:
            if ' (W-L-D)' in text:
                record, _ = text.split(' (')
                dictio.update(dict(zip(['WIN', 'LOSSES', 'DRAWS'], map(int, record.split('-')))))
            else:
                dictio.update({
                    "DIVISION": text,
                    "GENRE": "Female" if "Women's" in text else "Male"
                })
    
    return True if "WIN" in dictio.keys() else False
    



def _combattant_actif(driver : webdriver.Chrome, dictio: defaultdict) -> None :
    """
    Fonction qui determine si un combattant est actif ou non
    """

    if any(
        "Actif" in tag.text for tag in driver.find_elements(By.CSS_SELECTOR, "p.hero-profile__tag")
    ):
        dictio["Actif"] = True
    else:
        dictio["Actif"] = False


def _bio_combattant(driver : webdriver.chrome , dictio: defaultdict) -> None:
    """
    Fonction qui extrait les informations biographiques d'un combattant
    """
    required = [
        "STYLE DE COMBAT",
        "ÂGE",
        "LA TAILLE" ,
        "POIDS" ,
        "DÉBUT DE L'OCTOGONE",
        "REACH",
        "PORTÉE DE LA JAMBE",
    ]

    labels = driver.find_elements(By.CSS_SELECTOR, "div.c-bio__label")
    texts = driver.find_elements(By.CSS_SELECTOR, "div.c-bio__text")

    for lbl, txt in zip(labels, texts):
        lbl_text = lbl.text.strip() if lbl else None
        txt_content = txt.text.strip() if txt else None
        if lbl_text and lbl_text in required:
            div_emboitee = None
            try:
                div_emboitee = txt.find_element(By.CSS_SELECTOR, "div")
            except Exception:
                pass 
            
            val = div_emboitee.text.strip() if div_emboitee else txt_content
            
            if val:
                dictio[lbl_text] = (
                    float(val) if re.fullmatch(r"\d+(\.\d+)?", val) else val
                )




def _tenant_titre(driver, dictio: defaultdict) -> None:
    """
    Fonction qui determine si un combattant est le tenant du titre
    """

    if any(
        "Title Holder" in tag.text
        for tag in driver.find_elements(By.CSS_SELECTOR, "p.hero-profile__tag")
    ):
        dictio["Title_holder"] = True
    else:
        dictio["Title_holder"] = False


def _stats_combattant(driver, dictio: defaultdict):
    """
    Fonction qui extrait les statistiques d'un combattant
    """

    liste_objective = ["PERMANENT", "CLINCH", "SOL", "KO/TKO", "DEC", "SUB"]
    groups = driver.find_elements(By.CSS_SELECTOR, "div.c-stat-3bar__group")
    if groups:
        for group in groups:
            label = group.find_element(By.CSS_SELECTOR, "div.c-stat-3bar__label")
            value = group.find_element(By.CSS_SELECTOR, "div.c-stat-3bar__value")
            if label and value:
                cleaned_value = re.sub(r"\s*\(.*?\)", "", value.text).strip()
                dictio[label.text.strip()] = int(cleaned_value)
            else:
                dictio[label.text.strip()] = None
    else:
        for obj in liste_objective:
            dictio[obj] = None


def _stats_corps_combattant(driver, dictio: defaultdict) -> None:
    """
    Fonction qui extrait les statistiques de corps d'un combattant
    """

    # ['sig_str_head', 'sig_str_body', 'sig_str_leg']
    body_part = ["head", "body", "leg"]
    for part in body_part:
        
        btext_elements = driver.find_elements(By.CSS_SELECTOR, f"g#e-stat-body_x5F__x5F_{part}-txt")
        
        if btext_elements:
            btext = btext_elements[0] 
            texts = btext.find_elements(By.TAG_NAME, "text")
            
            if len(texts) > 1:
                dictio[f"sig_str_{part}"] = int(texts[1].text.strip())  # 1 On prend l'entier , mettre 0 pour prendre le pourcentage

        else:
            dictio[f"sig_str_{part}"] = None
    


def _pourcentage_touche_takedown(driver,  dictio: defaultdict) -> None:
    """
    Fonction qui extrait les pourcentages de takedown et de saisie d'un combattant
    """

    liste_objective = ["PRÉCISION SAISISSANTE", "PRÉCISION DE TAKEDOWN"]

    labels = driver.find_elements(By.CSS_SELECTOR, "h2.e-t3")
    pourcentage_text = driver.find_elements(By.CLASS_NAME, "e-chart-circle__percent")

    for titre, pourcentage in zip(labels, pourcentage_text):
        dictio[f"{titre.text}"] = float(pourcentage.text.rstrip("%")) / 100
    mot_manquants = [mot for mot in liste_objective if mot not in dictio.keys()]
    if mot_manquants:
        for mot in mot_manquants:
            dictio[f"{mot}"] = None


def _convert_minutes(time_str: str) -> float | None:
    """
    Fonction qui convertit le temps de combat moyen en secondes
    """

    try:
        minutes, secondes = map(int, time_str.split(":"))
        return minutes * 60 + secondes
    except ValueError:
        return None


def _mesures_combattant(driver, dictio: defaultdict) -> None:
    """
    Fonction qui extrait les mesures d'un combattant
    """

    liste_objective = ['SIG. STR. A ATTERRI', 
                       'SIG. FRAPPES ENCAISSÉES', 
                       'TAKEDOWN AVG', 'ENVOI AVG', 
                       'SIG. STR.DÉFENSE', 
                       'DÉFENSE DE DÉMOLITION', 
                       'KNOCKDOWN AVG', 
                       'TEMPS DE COMBAT MOYEN']


    temp_data = {}

    groups = driver.find_elements(By.CSS_SELECTOR, "div.c-stat-compare__group")

    for group in groups:

        label = group.find_element(By.CSS_SELECTOR, "div.c-stat-compare__label").text.strip()

        try :
            value = group.find_element(By.CSS_SELECTOR, "div.c-stat-compare__number").text.strip()
        except Exception:
            value = None

        if label and value:
            if ":" in value:
                temp_data[label] = _convert_minutes(value)
            elif "%" in value:
                temp_data[label] = float(re.sub(r"[^\d.]+", "", value).rstrip("%")) / 100
            else:
                temp_data[label] = float(re.sub(r"[^\d.]+", "", value))
        else :
            temp_data[label] = None
    
    for obj in liste_objective:
        dictio[obj] = temp_data.get(obj, None)  # Pour eviter les eventuelles decalages


def _recolte_image(driver : webdriver.Chrome, dictio : dict) -> None:
    """
    Fonction qui recolte l'image d'un combattant
    """
    image = driver.find_elements(By.CSS_SELECTOR,"div.hero-profile__image-wrap > img")
    if image:
        dictio["img_cbt"] = image[0].get_attribute("src")
    else :
        dictio["img_cbt"] = "NO" 


def _extraire_info_combattant(driver: webdriver.Chrome) -> defaultdict:
    """
    Permet d'extraire les informations d'un combattant a partir d'un objet BeautifulSoup

    Args:
        soup (BeautifulSoup): Objet BeautifulSoup de la page web du combattant

    Returns:
        dict: Dictionnaire contenant les informations du combattant

    """
    dictio = defaultdict(str)

    cbt_name = driver.find_element(By.CSS_SELECTOR, "div.hero-profile > div.hero-profile__info > h1").text

    if not cbt_name:
        return None

    dictio["NAME"] = cbt_name

    verif = _infos_principal_combattant(driver, dictio)
    if verif:
        _combattant_actif(driver, dictio)
        _bio_combattant(driver, dictio)
        _tenant_titre(driver, dictio)
        _stats_combattant(driver, dictio)
        _stats_corps_combattant(driver, dictio)
        _pourcentage_touche_takedown(driver, dictio)
        _mesures_combattant(driver, dictio)
        _recolte_image(driver, dictio)
    else: 
        return None
    return dictio


if __name__ == "__main__":

    console = Console()

    driver = webdriver.Chrome()

    url = "https://www.ufc.com/athlete/hamdy-abdelwahab"

    driver.get(url)

    dictio = _extraire_info_combattant(driver)

    console.print(dictio)

    driver.quit()
