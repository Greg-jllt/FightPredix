"""
Librairie pour nettoyer les données de Tapology

Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

import polars as pl
import json
import rapidfuzz as rf
from geopy.geocoders import Nominatim
from datetime import datetime
from .outils import configure_logger

date = datetime.now().strftime("%Y-%m-%d")
logger = configure_logger(f"{date}_crawler_clean_tapology")

def _manage_na(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui gère les données manquantes qui ne sont pas notées comme tel
    """

    return data_tapology.with_columns(
        pl.when(pl.col(col) == "N/A").then(None).otherwise(pl.col(col)).alias(col)
        for col in data_tapology.columns
    )


def _create_streaks_variables(data_tapology: pl.DataFrame) -> pl.DataFrame:
    """
    Fonction qui créer les variables de séries de performances
    """
    liste_number_streak: list[int | None] = []
    liste_type_streak: list[str | None] = []
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
    logger.info("Récupération des données")
    with open("Data/data_tapology.json", "r") as f:
        data_tapology = pl.DataFrame(json.load(f))

    with open("FightPredix_scraping/scraping/dico_formatage/dico_correction.json", "r") as f:
        dico_correction = json.load(f)

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
    data_tapology.to_pandas().to_csv("Data/clean_tapology.csv")
