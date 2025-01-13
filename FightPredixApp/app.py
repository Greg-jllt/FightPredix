import base64
import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import joblib
import requests
from PIL import Image
import time
import re


from pages import page_predictions
from rapidfuzz import fuzz
from style import init_pages, bouton_prediction
from datetime import datetime

init_pages()


def _calcul_nb_mois_dernier_combat(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction qui calcule les victoires des combattants au moment du combat
    """
    cob = combats.copy()
    cob = cob.sort_index(ascending=False)

    temp_dict: dict = {}

    def _sub_nb_mois_dernier_combat(combattant, nickname, prefixe):
        if f"{combattant}_{nickname}_date" not in temp_dict.keys():
            temp_dict[f"{combattant}_{nickname}_date"] = []

        temp_dict[f"{combattant}_{nickname}_date"].append(date)

        if len(temp_dict[f"{combattant}_{nickname}_date"]) > 2:
            temp_dict[f"{combattant}_{nickname}_date"].pop(0)

        cob.loc[i, f"{prefixe}_nb_mois_dernier_combat"] = (
            round(
                (
                    datetime.strptime(
                        temp_dict[f"{combattant}_{nickname}_date"][1], "%Y-%m-%d"
                    )
                    - datetime.strptime(
                        temp_dict[f"{combattant}_{nickname}_date"][0], "%Y-%m-%d"
                    )
                ).days
                / 30
            )
            if len(temp_dict[f"{combattant}_{nickname}_date"]) == 2
            else 0
        )

    for i, combat in cob.iterrows():
        combattant_1, nickname_1 = combat["combattant_1"], combats["nickname_1"]
        combattant_2, nickname_2 = combat["combattant_2"], combats["nickname_2"]
        date = combat["date"]

        nickname_1 = nickname_1 if isinstance(nickname_1, str) else "NO"
        nickname_2 = nickname_2 if isinstance(nickname_2, str) else "NO"

        _sub_nb_mois_dernier_combat(combattant_1, nickname_1, "combattant_1")
        _sub_nb_mois_dernier_combat(combattant_2, nickname_2, "combattant_2")

    cob = cob.sort_index(ascending=True)

    return cob

def _difference_num_combats(combats: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction de calcul de la différence entre les caractéristiques des combattants
    au sein de chaque combat.
    """

    cols_to_drop = []
    colonnes_a_concat = {}

    num_colonnes_combats = combats.select_dtypes(include=["number"]).columns

    pattern = re.compile(r"combattant_(\d+)_(.+)")

    for col in num_colonnes_combats:
        match = pattern.match(col)
        if match:
            stat_type = match.group(2)
            colonnes_a_concat[f"diff_{stat_type}"] = (
                combats[f"combattant_1_{stat_type}"]
                - combats[f"combattant_2_{stat_type}"]
            )
            cols_to_drop.append(f"combattant_1_{stat_type}")
            cols_to_drop.append(f"combattant_2_{stat_type}")

    df_numerique = pd.DataFrame(colonnes_a_concat, index=combats.index)

    resultat = pd.concat([combats.reset_index(drop=True), df_numerique], axis=1)

    # if cols_to_drop:
    #     Console().print(f"Colonnes à supprimer : {len(cols_to_drop)}")
    #     resultat.drop(cols_to_drop, axis=1, inplace=True)

    return resultat



def _liste_features() -> tuple[list[str], list[str], list[str]]:
    """
    Renvoie des listes de variables utilisables pour le machine learning
    """

    numeric_features = [
        "diff_age_t",
        "diff_win_t",
        "diff_losses_t",
        "diff_forme",
        "diff_serie",
        "diff_Sig_str_total_reussi_moyenne",
        "diff_Sig_str_total_total_moyenne",
        "diff_Total_str_total_reussi_moyenne",
        "diff_Total_str_total_total_moyenne",
        "diff_Tdtotal_reussi_moyenne",
        "diff_Tdtotal_total_moyenne",
        "diff_Headsig_str_total_reussi_moyenne",
        "diff_Headsig_str_total_total_moyenne",
        "diff_Bodysig_str_total_reussi_moyenne",
        "diff_Bodysig_str_total_total_moyenne",
        "diff_Legsig_str_total_reussi_moyenne",
        "diff_Legsig_str_total_total_moyenne",
        "diff_Distancesig_str_total_reussi_moyenne",
        "diff_Distancesig_str_total_total_moyenne",
        "diff_Clinchsig_str_total_reussi_moyenne",
        "diff_Clinchsig_str_total_total_moyenne",
        "diff_Groundsig_str_total_reussi_moyenne",
        "diff_Groundsig_str_total_total_moyenne",
        "diff_frappe_tete_moyenne",
        "diff_frappe_corps_moyenne",
        "diff_frappe_jambe_moyenne",
        "diff_frappe_distance_moyenne",
        "diff_frappe_clinch_moyenne",
        "diff_frappe_sol_moyenne",
        "diff_KDtotal_moyenne",
        "diff_Sig_str_total_ratio_moyenne",
        "diff_Sig_str_percent_total_moyenne",
        "diff_Total_str_total_ratio_moyenne",
        "diff_Tdtotal_ratio_moyenne",
        "diff_Td_percent_total_moyenne",
        "diff_Sub_atttotal_moyenne",
        "diff_Revtotal_moyenne",
        "diff_Ctrltotal_moyenne",
        "diff_Headsig_str_total_ratio_moyenne",
        "diff_Bodysig_str_total_ratio_moyenne",
        "diff_Legsig_str_total_ratio_moyenne",
        "diff_Distancesig_str_total_ratio_moyenne",
        "diff_Clinchsig_str_total_ratio_moyenne",
        "diff_Groundsig_str_total_ratio_moyenne",
        "diff_la_taille",
        "diff_poids",
        "diff_reach",
        "diff_portee_de_la_jambe",
        "diff_nb_mois_dernier_combat",
        "diff_DEC",
        "diff_KO/TKO",
        "diff_SUB",
    ]

    categorical_features = [
        "combattant_1_style_de_combat",
        "combattant_2_style_de_combat",
        "combattant_1_country_of_residence_tapology",
        "combattant_2_country_of_residence_tapology",
        "combattant_1_country_of_birth_tapology",
        "combattant_2_country_of_birth_tapology"
    ]

    output_feature = ["resultat", "poids_ml"]

    return numeric_features, categorical_features, output_feature


@st.cache_resource
def load_model():
    return joblib.load("model.pkl")

if os.path.exists("model.pkl"):
    model = load_model()

# Gestion de l'état pour suivre la page courante
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Page par défaut

# Navbar avec boutons Streamlit
def navbar():

    col1 = st.columns(1)[0]
    with col1:
        st.image("./img/logo_readme.png", width=100)

    col2, col3, col4 = st.columns(3, gap="small")

    with col2:
        if st.button("Accueil", key="home"):
            st.session_state.current_page = "home"
    # with col5:
    #     if st.button("Contact", key="contact"):
    #         st.session_state.current_page = "contact"

    with col3:
        if st.button("Combattants", key="combattants"):
            st.session_state.current_page = "combattants"

    with col4:
        if st.button("Prédictions", key="predictions"):
            st.session_state.current_page = "predictions"

navbar()

def navbar_sidebar():

    st.sidebar.title("Navigation")
    col1, col2, col3 = st.sidebar.columns(3, gap="small")

    with col1:
        if st.sidebar.button("Accueil", key="home_sidebar"):
            st.session_state.current_page = "home"

    with col2:
        if st.sidebar.button("Combattants", key="combattants_sidebar"):
            st.session_state.current_page = "combattants"

    with col3:
        if st.sidebar.button("Prédictions", key="predictions_sidebar"):
            st.session_state.current_page = "predictions"


def titre(texte):
    return st.markdown(
        f"""
        <p style="font-family:IM Fell Great Primer SC; font-size: 45px;">
        {texte}
        </p>
        """,
        unsafe_allow_html=True,
    )

# navbar_sidebar()

if "predictable" not in st.session_state:
        st.session_state["predictable"] = False

if st.session_state.current_page == "home":
    _, cent_co,_ = st.columns([1.5,1, 1])

    with cent_co:
        st.image(os.path.join("img", "logo.png"), width=350)

    titre("Bienvenue sur FightPredix !")
    st.write("FightPredix est une application développé avec python dans le but d'essayer de prédire les résultats des combats de L'UFC.")
    st.write("La section combattants permet de comparer deux combattants et de voir leurs statistiques respectives. Une fois la sélèction effectué cliquez sur le logo.")
    st.write("Enfin la section prédictions, comme son nom l'indique, permet de prédire le résultat d'un combat entre deux combattants.")


elif st.session_state.current_page == "combattants":
     
    _, cent_co,_ = st.columns([1.5,1, 1])

    with cent_co:
        titre("Section Combattants") 

    st.markdown(
    """
    <style>
        .vs-text {
            font-size: 50px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

    if "fighters" not in st.session_state:
        st.session_state["fighters"] = False

    if "fighter_1" not in st.session_state:
        st.session_state["fighter_1"] = "None"

    if "fighter_2" not in st.session_state:
        st.session_state["fighter_2"] = "None"

    if "url_1" not in st.session_state:
        st.session_state["url_1"] = "None"

    if "url_2" not in st.session_state:
        st.session_state["url_2"] = "None"

    file_path = os.path.join("Data/Data_final_fighters_V.csv")

    a1,a2 = st.columns([0.5, 1])

    if os.path.exists(file_path):

        df = pd.read_csv(file_path)
 
        df = df.dropna(subset=["actif"])
        df = df[df["actif"] == True]

        with a1:

            division = st.selectbox("Catégorie", list(df["division"].unique()))

            df = df[df["division"] == division]

            col1, col2, col3 = st.columns([1.5, 0.5, 1.5])

            options = list(df["name"])
            options.insert(0, "None")

            with col1:
                st.session_state["fighter_1"] = st.selectbox("Combattant 1", options)
                fighter_1 = st.session_state["fighter_1"]
                if fighter_1 != "None":
                    st.session_state["url_1"] = df.loc[df['name'] == fighter_1, 'img_cbt'].iloc[0]
                    if st.session_state["url_1"] == "NO":
                        st.session_state["url_1"] = os.path.join("img", "fighter.png")
                    col1.image(st.session_state["url_1"], width=300)

            with col2:
                col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)


            with col3:
                st.session_state["fighter_2"] = col3.selectbox("Combattant 2", options)
                fighter_2 = st.session_state["fighter_2"]
                if fighter_2 != "None":
                    st.session_state["url_2"] = df.loc[df['name'] == fighter_2, 'img_cbt'].iloc[0]
                    if st.session_state["url_2"] == "NO":
                        st.session_state["url_2"] = os.path.join("img", "fighter.png")
                    col3.image(st.session_state["url_2"], width=300)

            if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
                titre("Choisissez deux combattants différents.")
                st.session_state["predictable"] = False
            else :
                with col2 :
                    # col2.markdown("<br><br><br><br><br>", unsafe_allow_html=True)  # Deux sauts de ligne HTML
                    if col2.button("", key="predict"):
                        st.session_state["predictable"] = True

            with a2:

                df_filtre = df[["name",'précision_saisissante','précision_de_takedown','sig_str_défense','défense_de_démolition']]

                df_filtre.rename(columns={
                    'précision_saisissante': 'strike acccuracy',
                    'précision_de_takedown': 'takedown accuracy',
                    'sig_str_défense': 'strike defense',
                    'défense_de_démolition': ' takedown defense'
                })

                categories =['strike acccuracy', 'takedown accuracy', 'strike defense', ' takedown defense']

                fig_1 = go.Figure()
                for name in [fighter_1, fighter_2]:
                    if name != "None":
                        person_data = df_filtre[df_filtre['name'] == name].iloc[0, 1:].tolist()
                    else :
                        person_data = [0, 0, 0, 0]
                    fig_1.add_trace(go.Scatterpolar(
                        r=person_data,
                        theta=categories + [categories[0]],
                        fill='toself',
                        name=name
                    ))

                fig_1.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=True,
                    height=500,
                    width=700,
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    annotations=[
                        dict(
                            x=1.20,
                            y=0,
                            xref="paper",
                            yref="paper",
                            text="strike accuracy: Le pourcentage de coups réussis.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        ),
                        dict(
                            x=1.20,
                            y=-0.05,
                            xref="paper",
                            yref="paper",
                            text="takedown accuracy: Le pourcentage de takedown réussies.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        ),
                        dict(
                            x=1.20,
                            y=-0.10,
                            xref="paper",
                            yref="paper",
                            text="strike defense: Le pourcentage de coups bloqués.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        ),
                        dict(
                            x=1.20,
                            y=-0.15,
                            xref="paper",
                            yref="paper",
                            text="takedown defense: Le pourcentage de takedown bloqués.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        ),
                        dict(
                            x=0,
                            y=-0.2,
                            xref="paper",
                            yref="paper",
                            text="NB : Des données peuvent ne pas être disponibles.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        )
                    ]
                )

                fig_2 = go.Figure()

                for name in [fighter_1, fighter_2]:
                    if name != "None":
                        person_data = df[(df['name'] == name) ][["sig_str_head", "sig_str_body", "sig_str_leg"]].iloc[0].tolist()
                        fig_2.add_trace(go.Bar(
                            x=["frappe tête", "frappe corp", "frappe jambes"],
                            y=person_data,
                            name=name
                        ))

                fig_2.update_layout(
                    barmode='group',
                    height=500,
                    width=700,
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)',
                    annotations=[
                        dict(
                            x=0.5,
                            y=-0.2,
                            xref="paper",
                            yref="paper",
                            text="NB : Des données peuvent ne pas être disponibles.",
                            showarrow=False,
                            font=dict(size=12),
                            align="center"
                        )
                    ]
                )

                e1, e2 = st.columns([1, 1])

                with e1:
                    st.plotly_chart(fig_1, use_container_width=True)

                with e2:
                    st.plotly_chart(fig_2, use_container_width=True)

                data = df.loc[(df["name"] == fighter_1) | (df["name"] == fighter_2), ["name", "poids", "âge","win","losses", "draws", "ko_tko", "sub", "dec"]] #"LA TAILLE"
                data.set_index("name", inplace=True)
                data = data.round(1)
                st.table(data.style.format("{:.0f}"))

elif st.session_state.current_page == "predictions":
    # page_predictions()
    if st.session_state["predictable"] == False:
        titre("Choisissez deux combattants différents.")
    else:
        DataFighters = pd.read_csv("Data/Data_final_fighters_V.csv", encoding="utf-8")
        DataCombats = pd.read_csv("Data/Data_final_combats_V.csv", encoding="utf-8")

        DataCombats = _calcul_nb_mois_dernier_combat(DataCombats)

        num_features, cat_features, output_features = _liste_features()

        predictions = []

        DataCombats.rename(columns={"diff_portÃ©e_de_la_jambe": "diff_portee_de_la_jambe"}, inplace=True)
        DataFighters.rename(columns={"portée_de_la_jambe": "portee_de_la_jambe", "âge": "age"}, inplace=True)  

        indice_nom1 = DataFighters[DataFighters["name"] == st.session_state["fighter_1"]].index[0]
        indice_nom2 = DataFighters[DataFighters["name"] == st.session_state["fighter_2"]].index[0]

        for num1, num2 in zip((indice_nom1,indice_nom2), (indice_nom2,indice_nom1)):
            Combattant_1 = pd.DataFrame(DataFighters.loc[num1]).T
            Combattant_2 = pd.DataFrame(DataFighters.loc[num2]).T
            
            Combattant_1.columns = [
                "combattant_1" + str(col) if "moyenne" in col else "combattant_1_" + str(col)
                for col in Combattant_1.columns
            ]
            Combattant_2.columns = [
                "combattant_2" + str(col) if "moyenne" in col else "combattant_2_" + str(col)
                for col in Combattant_2.columns
            ]
            Combattant_1["join_key"] = "1"
            Combattant_2["join_key"] = "1"
            
            combat = Combattant_1.merge(Combattant_2, on="join_key")
            Data_combattant_1 = pd.DataFrame()
            Data_combattant_2 = pd.DataFrame()
            
            nom1 = DataFighters.loc[num1, "name"]
            nom2 = DataFighters.loc[num2, "name"]

            for c1, c2 in zip(DataCombats["combattant_1"], DataCombats["combattant_2"]):
                # Comparer avec le premier combattant
                if nom1.lower() == c1.lower():
                    Data_combattant_1 = pd.concat([Data_combattant_1, DataCombats[DataCombats["combattant_1"] == c1]])
                elif fuzz.ratio(nom1.lower(), c1.lower()) >= 90:
                    Data_combattant_1 = pd.concat([Data_combattant_1, DataCombats[DataCombats["combattant_1"] == c1]])
                
                if nom1.lower() == c2.lower():
                    Data_combattant_1 = pd.concat([Data_combattant_1, DataCombats[DataCombats["combattant_2"] == c2]])
                elif fuzz.ratio(nom1.lower(), c2.lower()) >= 90:
                    Data_combattant_1 = pd.concat([Data_combattant_1, DataCombats[DataCombats["combattant_2"] == c2]])

                # Comparer avec le seizième combattant
                if nom2.lower() == c1.lower():
                    Data_combattant_2 = pd.concat([Data_combattant_2, DataCombats[DataCombats["combattant_1"] == c1]])
                elif fuzz.ratio(nom2.lower(), c1.lower()) >= 90:
                    Data_combattant_2 = pd.concat([Data_combattant_2, DataCombats[DataCombats["combattant_1"] == c1]])
                
                if nom2.lower() == c2.lower():
                    Data_combattant_2 = pd.concat([Data_combattant_2, DataCombats[DataCombats["combattant_2"] == c2]])
                elif fuzz.ratio(nom2.lower(), c2.lower()) >= 90:
                    Data_combattant_2 = pd.concat([Data_combattant_2, DataCombats[DataCombats["combattant_2"] == c2]])

            Data_combattant_1.drop_duplicates(inplace=True)
            Data_combattant_1.sort_index(inplace=True)
            Data_combattant_2.drop_duplicates(inplace=True)
            Data_combattant_2.sort_index(inplace=True)


            if nom1.lower() == Data_combattant_1["combattant_1"].iloc[0].lower() or nom1.lower() == Data_combattant_1["combattant_2"].iloc[0].lower():
                combattant_1_forme = Data_combattant_1["combattant_1_forme"].iloc[0]
                combattant_1_serie = Data_combattant_1["combattant_1_serie"].iloc[0]
                combattant_1_nb_mois = Data_combattant_1["combattant_1_nb_mois_dernier_combat"].iloc[0]
            elif fuzz.ratio(nom1.lower(), Data_combattant_1["combattant_1"].iloc[0].lower()) >= 90 or fuzz.ratio(nom1.lower(), Data_combattant_1["combattant_2"].iloc[0].lower()) >= 90:
                combattant_1_forme = Data_combattant_1["combattant_2_forme"].iloc[0]
                combattant_1_serie = Data_combattant_1["combattant_2_serie"].iloc[0]
                combattant_1_nb_mois = Data_combattant_1["combattant_2_nb_mois_dernier_combat"].iloc[0]
                
            if nom2.lower() == Data_combattant_2["combattant_1"].iloc[0].lower() or nom2.lower() == Data_combattant_2["combattant_2"].iloc[0].lower():
                combattant_2_forme = Data_combattant_2["combattant_1_forme"].iloc[0]
                combattant_2_serie = Data_combattant_2["combattant_1_serie"].iloc[0]
                combattant_2_nb_mois = Data_combattant_2["combattant_1_nb_mois_dernier_combat"].iloc[0]
            elif fuzz.ratio(nom2.lower(), Data_combattant_2["combattant_1"].iloc[0].lower()) >= 90 or fuzz.ratio(nom2.lower(), Data_combattant_2["combattant_2"].iloc[0].lower()) >= 90:
                combattant_2_forme = Data_combattant_2["combattant_2_forme"].iloc[0]
                combattant_2_serie = Data_combattant_2["combattant_2_serie"].iloc[0]
                combattant_2_nb_mois = Data_combattant_2["combattant_2_nb_mois_dernier_combat"].iloc[0]
                
            combat.loc[0, "combattant_1_forme"] = combattant_1_forme
            combat.loc[0, "combattant_1_serie"] = combattant_1_serie
            combat.loc[0, "combattant_2_forme"] = combattant_2_forme
            combat.loc[0, "combattant_2_serie"] = combattant_2_serie
            combat.loc[0, "combattant_1_nb_mois_dernier_combat"] = combattant_1_nb_mois
            combat.loc[0, "combattant_2_nb_mois_dernier_combat"] = combattant_2_nb_mois
            
            var_moyenne = [col for col in combat.columns if "moyenne" in col]

            var_num_en_plus = [
                "combattant_1_win",
                "combattant_1_losses",
                "combattant_1_age",
                "combattant_1_la_taille",
                "combattant_1_poids",
                "combattant_1_reach",
                "combattant_1_portee_de_la_jambe",
                "combattant_2_win",
                "combattant_2_losses",
                "combattant_2_age",
                "combattant_2_la_taille",
                "combattant_2_poids",
                "combattant_2_reach",
                "combattant_2_portee_de_la_jambe",
                "combattant_1_sol",
                "combattant_1_ko_tko",
                "combattant_1_dec",
                "combattant_1_sub",
                "combattant_2_sol",
                "combattant_2_ko_tko",
                "combattant_2_dec",
                "combattant_2_sub",
                "combattant_1_forme",
                "combattant_1_serie",
                "combattant_2_forme",
                "combattant_2_serie",
                "combattant_1_nb_mois_dernier_combat",
                "combattant_2_nb_mois_dernier_combat",
            ]

            cat_features = [
                "combattant_1_style_de_combat",
                "combattant_1_country_of_residence_tapology",
                "combattant_1_country_of_birth_tapology",
                "combattant_2_style_de_combat",
                "combattant_2_country_of_residence_tapology",
                "combattant_2_country_of_birth_tapology",
            ]
            
            liste_a_travailler = var_moyenne + var_num_en_plus + cat_features

            combat = combat[liste_a_travailler]
            
            type_mapping = {col: 'number' if col in var_num_en_plus + var_moyenne else 'object' for col in combat.columns}

            for col, dtype in type_mapping.items():
                if dtype == 'number':
                    combat[col] = combat[col].astype(float)  # Convertir en float pour les colonnes numériques
                else:
                    combat[col] = combat[col].astype(str)  # Convertir en string pour les colonnes catégorielles
            
            combat = _difference_num_combats(combat)
            
            combat.rename(columns={
                "diff_age" : "diff_age_t",
                "diff_win" : "diff_win_t",
                "diff_losses" : "diff_losses_t",
                "diff_dec" : "diff_DEC",
                "diff_ko_tko" : "diff_KO/TKO",
                "diff_sub" : "diff_SUB",
                }, inplace=True)
            
            import joblib

            model = joblib.load("./modele/LogisticRegression.pkl")
            
            predictions.append(model.predict_proba(combat[num_features + cat_features]))

        results = ((predictions[1].flatten()[0] + predictions[0].flatten()[0])/2 , (predictions[1].flatten()[1] + predictions[0].flatten()[1])/2)

        def download_and_convert_image(url, filename):
            if not os.path.exists('img'):
                os.makedirs('img')

            if url != "None":
                with open(filename, 'wb') as handle:
                    response = requests.get(url, stream=True)
                    if not response.ok: 
                        print(response)
                        return None
                    for block in response.iter_content(1024):
                        if not block:
                            break
                        handle.write(block)

                if os.path.exists(filename):
                    im = Image.open(filename)
                    png_filename = filename.replace('.jpg', '.png')
                    im.save(png_filename)
                    os.remove(filename)
                    return png_filename
            return None

        image_path_1 = download_and_convert_image(st.session_state.get("url_1", "None"), 'img/cbt1.jpg')
        image_path_2 = download_and_convert_image(st.session_state.get("url_2", "None"), 'img/cbt2 .jpg')

        if image_path_1 is not None and image_path_2 is not None:
            cbt1 = Image.open(image_path_1)
            cbt2  = Image.open(image_path_2)

        values = [results[0], results[1]]
        labels = [st.session_state["fighter_1"], st.session_state["fighter_2"]]
        imgs = [cbt1, cbt2]

        fig = go.Figure()

        fig.add_trace(go.Bar(x=labels, 
                             y=values, 
                             marker_color=['#00172B', '#00172B'],
                             opacity=1))

        fig.add_layout_image(
                dict(
                    source=cbt1,
                    xref="x domain",
                    yref="y domain",
                    x=0.75-1/2,
                    y=values[0]/2, 
                    layer="above",
                    xanchor="center",
                    yanchor="bottom", 
                    sizex=0.6,
                    sizey=0.6,
                )
            )
        
        fig.add_layout_image(
                dict(
                    source=cbt2,
                    xref="x domain",
                    yref="y domain",
                    x=0.75,
                    y=values[1]/2, 
                    layer="above",
                    xanchor="center",
                    yanchor="bottom", 
                    sizex=0.6,
                    sizey=0.6,
                )
            )


        fig.update_layout(
            title="",
            xaxis_title="",
            yaxis=dict(
                title=' ', 
                range=[0, 2],
                showticklabels=False, 
                showgrid=False        
            ),
            height=600,
            width=900,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            template="plotly_white"
        )

        _, cent_co,_ = st.columns([1,1, 1])
        with cent_co:
            with st.spinner('Prediction en cours'):
                time.sleep(6)
                st.plotly_chart(fig)
                st.write(f"Selon l'algorrithme, {st.session_state['fighter_1']} a une probabilité de vaincre {st.session_state['fighter_2']} de {round(values[0]*100)}%, la où {st.session_state['fighter_2']} a une probabilité de vaincre {st.session_state['fighter_1']} de {round(values[1]*100)}%.")


else:
        titre("Page non trouvée")
        st.write("La page demandée n'existe pas.")
