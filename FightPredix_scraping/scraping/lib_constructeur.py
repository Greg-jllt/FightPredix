"""
Librairie de fonctions pour la construction de la base de données
Développée par :
    - [Gregory Jaillet](https://github.com/Greg-jllt)
    - [Hugo Cochereau](https://github.com/hugocoche)
"""

from rapidfuzz import fuzz
from datetime import datetime


import pandas as pd



def _difference_combats(caracteristiques : pd.DataFrame, combats : pd.DataFrame) -> pd.DataFrame :
    """
    Fonction qui calcule la difference entre les caracteristiques des combattants
    """
    
    for i, combat in combats.iterrows():

        combattant_1 = combat["combattant_1"]
        combattant_2 = combat["combattant_2"]

        for nom in caracteristiques["NAME"].values:
            if fuzz.ratio(nom.lower(), combattant_1.lower()) > 95:
                stats_combattant_1 = caracteristiques[caracteristiques["NAME"].str.lower() == nom.lower()].iloc[0]
                break
        
        for nom in caracteristiques["NAME"].values:
            if fuzz.ratio(nom.lower(), combattant_2.lower()) > 95:
                stats_combattant_2 = caracteristiques[caracteristiques["NAME"].str.lower() == nom.lower()].iloc[0]
                break
    

        categorielles = caracteristiques.select_dtypes(include=["object"]).columns
        numeric_columns = caracteristiques.select_dtypes(include=["number"]).columns

        for column in numeric_columns:

            if isinstance(stats_combattant_1[column], (int, float)) and isinstance(stats_combattant_2[column], (int, float)):
                combats.loc[i, f"diff_{column}"] = stats_combattant_1[column] - stats_combattant_2[column]

        for column in categorielles.drop(["NAME"]):
            combats.loc[i, f"{column}_1"] = stats_combattant_1[column]
            combats.loc[i, f"{column}_2"] = stats_combattant_2[column]

    return combats


def _age_by_DOB(Data):

    data = Data[Data["ÂGE"].isna()& Data["DOB"].notna()]

    for _, cbt in data.iterrows():
        cbt_name = cbt["NAME"].upper()

        dob = data[data["NAME"] == cbt_name]["DOB"].values[0]
        if pd.notna(dob):
            Age = (datetime.now() - datetime.strptime(dob, '%b %d, %Y')).days // 365
            Data.loc[Data["NAME"] == cbt_name, "ÂGE"] = Age
    return Data


def _transformation_debut_octogone(data):
    data["DÉBUT_DE_L_OCTOGONE_1"] = data["DÉBUT_DE_L_OCTOGONE_1"].astype(str)
    data["DÉBUT_DE_L_OCTOGONE_2"] = data["DÉBUT_DE_L_OCTOGONE_2"].astype(str)
    data["DÉBUT_DE_L_OCTOGONE_1"] = pd.to_datetime(data["DÉBUT_DE_L_OCTOGONE_1"])
    data["DÉBUT_DE_L_OCTOGONE_2"] = pd.to_datetime(data["DÉBUT_DE_L_OCTOGONE_2"])
    data["DÉBUT_DE_L_OCTOGONE_1"] = (pd.to_datetime("today") - data["DÉBUT_DE_L_OCTOGONE_1"]).dt.days // 12
    data["DÉBUT_DE_L_OCTOGONE_2"] = (pd.to_datetime("today") - data["DÉBUT_DE_L_OCTOGONE_2"]).dt.days // 12

    data["diff_debut_octogone"] = data["DÉBUT_DE_L_OCTOGONE_1"] - data["DÉBUT_DE_L_OCTOGONE_2"]

    data.drop(columns=["DÉBUT_DE_L_OCTOGONE_1", "DÉBUT_DE_L_OCTOGONE_2"], inplace=True)
    
    return data