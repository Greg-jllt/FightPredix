from .lib_front_page import page_principal_UFC
from .lib_combats import main_combat_recolte
from .lib_ufc_stats import cherche_combattant_UFC_stats

def Dataframe_caracteristiques():

    Data = page_principal_UFC()

    Data = cherche_combattant_UFC_stats(Data)

    Data = ...

    Data.to_csv("ufc_fighters_carac.csv", index=False)

    return Data

def Dataframe_combats():

    Data = main_combat_recolte()

    Data.to_csv("ufc_fights_combats.csv", index=False)

    return Data