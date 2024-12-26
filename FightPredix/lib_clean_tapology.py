"""
Librairie pour nettoyer les données de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from venv import logger
import polars as pl
import json
import os
import sys
import rapidfuzz as rf
from geopy.geocoders import Nominatim
from datetime import datetime
from .lib_scraping_tapology import _init_logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _manage_na(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui gère les données manquantes qui ne sont pas notées comme tel
    """

    return data_tapology.with_columns(
        pl.when(pl.col(col) == "N/A").then(None).otherwise(pl.col(col)).alias(col)
        for col in data_tapology.columns
    )


def get_closest_streak(streak: str, streaks: list[str]) -> str | None:
    if streak != "N/A":
        number_streak, _ = streak.split(" ")
        return rf.process.extractOne(number_streak, streaks)[0]
    else:
        return None


def _create_streaks_variables(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui créer les variables de séries de performances
    """
    liste_number_streak = []
    liste_type_streak = []
    liste_current_win_streak = []
    liste_current_lose_streak = []

    for streak in data_tapology["Current MMA Streak:tapology"]:
        if not streak:
            liste_number_streak.append(None)
            liste_type_streak.append(None)
        else:
            number_streak, type_streak = streak.split(" ")
            liste_number_streak.append(int(number_streak))
            liste_type_streak.append(
                rf.process.extractOne(type_streak, ["win", "loss"])[0]
            )

    liste_current_win_streak = [
        number if type_streak == "win" else 0 if type_streak == "loss" else None
        for number, type_streak in zip(liste_number_streak, liste_type_streak)
    ]
    liste_current_lose_streak = [
        number if type_streak == "loss" else 0 if type_streak == "win" else None
        for number, type_streak in zip(liste_number_streak, liste_type_streak)
    ]

    return data_tapology.with_columns(
        pl.Series("Current Win Streak:tapology", liste_current_win_streak),
        pl.Series("Current Lose Streak:tapology", liste_current_lose_streak),
    )


def _reformat_date(
    date_str: str, input_format: str = "%B %d, %Y", output_format: str = "%d/%m/%Y"
) -> str:
    """
    Fonction qui reformate la date
    """
    date_str = date_str.strip()
    date_obj = datetime.strptime(date_str, input_format)
    return date_obj.strftime(output_format)


def _create_last_fight_variables(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui créer les variables de la date du dernier combat
    """
    liste_date = []
    liste_place = []

    for date in data_tapology["Last Fight:tapology"]:
        if date:
            parts = date.split("\nin\n")
            if "20" in parts[0] or "19" in parts[0]:
                liste_date.append(date.split("\nin\n")[0].strip())
                if len(parts) > 1:
                    liste_place.append(parts[1].strip())
                else:
                    liste_place.append(None)
            else:
                liste_date.append(None)
                if len(parts) == 1:
                    liste_place.append(parts[0].strip())
        else:
            liste_date.append(None)
            liste_place.append(None)

    for index, date in enumerate(liste_date):
        if date:
            liste_date[index] = _reformat_date(date)

    return data_tapology.with_columns(
        pl.Series("Date of last fight:tapology", liste_date),
        pl.Series("Organization of last fight:tapology", liste_place),
    )


def _create_home_variables(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui créer les variables de la ville et du pays de résidence
    """
    geolocator = Nominatim(user_agent="python")
    list_lieu_de_residence = data_tapology["Fighting out of:tapology"].to_list()
    liste_country_of_residence = []
    liste_city_of_residence = []
    liste_state_of_residence = []

    for location in list_lieu_de_residence:
        if location:
            loc = geolocator.geocode(
                location.lower(), language="en", addressdetails=True, timeout=50
            )
            if loc:
                address = loc.raw["address"]
                if "country" in address.keys():
                    country = address.get("country")
                else:
                    country = None
                if "city" in address.keys():
                    city = address.get("city")
                else:
                    city = None
                if "state" in address.keys():
                    state = address.get("state")
                else:
                    state = None
                liste_country_of_residence.append(country)
                liste_city_of_residence.append(city)
                liste_state_of_residence.append(state)
            else:
                liste_country_of_residence.append(None)
                liste_city_of_residence.append(None)
                liste_state_of_residence.append(None)
        else:
            liste_country_of_residence.append(None)
            liste_city_of_residence.append(None)
            liste_state_of_residence.append(None)

    return data_tapology.with_columns(
        pl.Series("Country of residence:tapology", liste_country_of_residence),
        pl.Series("City of residence:tapology", liste_city_of_residence),
        pl.Series("State of residence:tapology", liste_state_of_residence),
    )


def _birth_country(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui créer la variable du pays de naissance
    """

    geolocator = Nominatim(user_agent="python")
    locations = data_tapology["Born:tapology"]
    liste_place_of_birth = []
    for location in locations:
        if location:
            loc = geolocator.geocode(
                location.lower(), language="en", addressdetails=True, timeout=50
            )
            if loc:
                address = loc.raw["address"]
                country = address.get("country")
                liste_place_of_birth.append(country)
            else:
                liste_place_of_birth.append(None)
        else:
            liste_place_of_birth.append(None)

    return data_tapology.with_columns(
        pl.Series("Country of birth:tapology", liste_place_of_birth)
    )


if __name__ == "__main__":
    logger = _init_logger()

    logger.info("Récupération des données")
    with open("../../donnees_finales/final_tapology.json", "r") as f:
        data_tapology = pl.DataFrame(json.load(f))

    data_tapology = data_tapology.unique()
    data_tapology = _manage_na(data_tapology)

    logger.info("Création des variables de séries de performances")
    data_tapology = _create_streaks_variables(data_tapology)

    logger.info("Création des variables de date de dernier combat")
    data_tapology = _create_last_fight_variables(data_tapology)

    logger.info("Création de la variable des gains")
    data_tapology = data_tapology.with_columns(
        pl.Series(
            "Career Disclosed Earnings (in $ USD):tapology",
            [
                int(disclosed.split(" ")[0].split("$")[1].replace(",", "").strip())
                for disclosed in data_tapology["Career Disclosed Earnings:tapology"]
            ],
        )
    )

    logger.info("Création des variables de résidence")
    data_tapology = _create_home_variables(data_tapology)

    logger.info("Création de la variable du pays de naissance")
    data_tapology = _birth_country(data_tapology)

    logger.info("Sélection des colonnes")
    data_tapology = data_tapology.select(
        [
            "NAME",
            "Date of last fight:tapology",
            "Organization of last fight:tapology",
            "Country of residence:tapology",
            "City of residence:tapology",
            "State of residence:tapology",
            "Country of birth:tapology",
            "Career Disclosed Earnings (in $ USD):tapology",
            "Affiliation:tapology",
            "Current Win Streak:tapology",
            "Current Lose Streak:tapology",
        ]
    ).unique()
    dico_correction = {
        "NAME": [
            "askar askar",
            "michael cora",
            "silva lopes",
            "leonardo de oliveira",
            "nick fiore",
            "luis gomez",
            "joey gomez",
            "luis henrique",
            "carlos hernandez",
            "sumit kumar",
            "malik lewis",
            "dan miller",
            "alex pereira",
            "bruno santos",
            "ronal siahaan",
            "bruno silva",
            "leandro silva",
            "jean silva",
            "willian souza",
            "anthony torres",
            "suyoung you",
            "jon jones",
            "henrique da silva lopes",
        ],
        "Date of last fight:tapology": [
            "30/09/2023",
            "26/01/2024",
            None,
            "01/06/2024",
            "17/08/2024",
            "20/05/2022",
            None,
            "23/12/2023",
            "23/11/2024",
            "27/07/2024",
            "06/10/2024",
            "12/07/2015",
            "05/10/2024",
            "09/06/2023",
            "20/04/2024",
            None,
            "09/11/2024",
            "13/07/2024",
            "16/03/2024",
            "26/01/2019",
            "23/11/2024",
            "16/03/2024",
            "23/08/2019",
        ],
        "Organization of last fight:tapology": [
            "LOC",
            "KC",
            None,
            "F2O",
            "CZ",
            "CG",
            None,
            "TCF",
            "UFC",
            None,
            "FFC",
            "UFC",
            "UFC",
            "BFL",
            "CWFC",
            None,
            "OKMMA",
            "UFC",
            "JFC",
            "FTW",
            "UFC",
            "UFC",
            "FFC",
        ],
        "Country of residence:tapology": [  # ici
            "United States",
            "United States",
            None,
            "Brazil",
            "United States",
            "Cuba",
            None,
            "Brazil",
            "United States",
            "United States",
            "United States",
            "United States",
            "United States",
            "Brazil",
            "Indonesia",
            None,
            "Brazil",
            "Brazil",
            "Brazil",
            "United States",
            "South Korea",
            "United States",
            "Brazil",
        ],
        "City of residence:tapology": [  # ici
            "Chicago",
            "Tampa",
            None,
            "Areia Branca",
            "Derry",
            None,
            None,
            "Rio de Janeiro",
            None,
            "Sacramento",
            "Fort Worth",
            "Whippany",
            "Bethel",
            "Salvador",
            "Bogor",
            None,
            "Sao Paulo",
            "Sao Paulo",
            "Sao Cristovao",
            None,
            "Gunpo-Si",
            "Albuquerque",
            "Belo Horizonte",
        ],
        "State of residence:tapology": [
            "Illinois",
            "Florida",
            None,
            "Rio Grande do Norte",
            "New Hampshire",
            None,
            None,
            "Rio de Janeiro",
            "Illinois",
            "California",
            "Texas",
            "New Jersey",
            "Connecticut",
            "Bahia",
            None,
            None,
            "Sao Paulo",
            None,
            "Sergipe",
            None,
            "Gyeonggi-Do",
            "New Mexico",
            "Minas Gerais",
        ],
        "Country of birth:tapology": [
            "Palestine",
            "United States",
            None,
            "Brazil",
            "United States",
            "Cuba",
            None,
            "Brazil",
            "United States",
            "India",
            "Germany",
            "United States",
            "Brazil",
            "Brazil",
            "Indonesia",
            None,
            "Brazil",
            "Brazil",
            "Brazil",
            "United States",
            "South Korea",
            "United States",
            "Brazil",
        ],
        "Career Disclosed Earnings (in $ USD):tapology": [
            0,
            5000,
            None,
            0,
            0,
            5000,
            None,
            26000,
            0,
            0,
            0,
            178000,
            300000,
            66000,
            0,
            None,
            78000,
            50000,
            0,
            10000,
            0,
            4618000,
            0,
        ],
        "Affiliation:tapology": [
            "Round 4 Gym",
            "Gracie Tampa",
            None,
            "Talison Soares Team",
            "New England Cartel",
            None,
            None,
            "Tata Fight Team",
            "VFS Academy",
            "Team Alpha Male",
            None,
            "AMA Fight Club",
            "Teixeira MMA & Fitness",
            None,
            "Synergy MMA Academy Bali",
            None,
            "American Top Team",
            "Fighting Nerds",
            "World Fight System",
            "MMAD",
            "Von Jiu Jitsu",
            "Jackson Wink MMA Academy",
            "BH Rhinos",
        ],
        "Current Win Streak:tapology": [
            0.0,
            0.0,
            None,
            3.0,
            3.0,
            0.0,
            None,
            3.0,
            0.0,
            1.0,
            1.0,
            0.0,
            5.0,
            0.0,
            0.0,
            None,
            1.0,
            11.0,
            2.0,
            0.0,
            3.0,
            19.0,
            0.0,
        ],
        "Current Lose Streak:tapology": [
            1.0,
            2.0,
            None,
            0.0,
            0.0,
            1.0,
            None,
            0.0,
            1.0,
            0.0,
            0.0,
            2.0,
            0.0,
            1.0,
            1.0,
            None,
            0.0,
            0.0,
            0.0,
            3.0,
            0.0,
            0.0,
            2.0,
        ],
    }

    ligne_a_remplacer = data_tapology.filter(
        pl.col("NAME").is_in(dico_correction["NAME"])
    )
    lignes_remplacement = pl.DataFrame(dico_correction)

    data_tapology = data_tapology.filter(
        ~pl.col("NAME").is_in(dico_correction["NAME"])
    ).vstack(lignes_remplacement)
    data_tapology = data_tapology.with_columns(
        pl.Series("NAME", [nom.upper() for nom in data_tapology["NAME"].to_list()])
    )
    data_tapology.to_pandas().to_csv("../../donnees_finales/final_clean_tapology.csv")
