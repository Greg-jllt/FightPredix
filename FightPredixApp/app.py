import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go
import joblib
from PIL import Image

from style import init_pages
from lib_streamlit import (
    _liste_features,
    _prediction_streamlit,
    _download_et_convert_image,
)

init_pages()


@st.cache_resource
def charger_model():
    return joblib.load("model.pkl")


if os.path.exists("model.pkl"):
    model = charger_model()

# Gestion de l'état pour suivre la page courante
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Page par défaut


# Navbar avec boutons Streamlit
def navbar():

    col1 = st.columns(1)[0]
    with col1:
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "img", "logo_readme.png"
        )
        st.image(image_path, width=100)

    col2, col3, col4 = st.columns(3, gap="small")

    with col2:
        if st.button("Accueil", key="home"):
            st.session_state.current_page = "home"

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
    _, cent_co, _ = st.columns([1.5, 1, 1])

    with cent_co:
        image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "img", "logo.png"
        )
        st.image(image_path, width=350)

    titre("Bienvenue sur FightPredix !")
    st.write(
        "FightPredix est une application développé avec python dans le but d'essayer de prédire les résultats des combats de L'UFC."
    )
    st.write(
        "La section combattants permet de comparer deux combattants et de voir leurs statistiques respectives. Une fois la sélèction effectué cliquez sur le logo."
    )
    st.write(
        "Enfin la section prédictions, comme son nom l'indique, permet de prédire le résultat d'un combat entre deux combattants."
    )


elif st.session_state.current_page == "combattants":

    _, cent_co, _ = st.columns([1.5, 1, 1])

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
    """,
        unsafe_allow_html=True,
    )

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

    fighters_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "DataApp",
        "Data_final_fighters.json",
    )
    fights_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "DataApp", "Data_final_combats.json"
    )
    a1, a2 = st.columns([0.5, 1])

    if "DataFighters" not in st.session_state:
        st.session_state["DataFighters"] = pd.read_json(fighters_path)

    if "DataCombats" not in st.session_state:
        st.session_state["DataCombats"] = pd.read_json(fights_path)

    df = st.session_state["DataFighters"]

    df = df.dropna(subset=["actif"])
    df = df[df["actif"] == True]  # flake8: noqa

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
                st.session_state["url_1"] = df.loc[
                    df["name"] == fighter_1, "img_cbt"
                ].iloc[0]
                if st.session_state["url_1"] == "NO":
                    st.session_state["url_1"] = os.path.join(
                        "FightPredixApp\img", "fighter.png"
                    )
                col1.image(st.session_state["url_1"], width=300)

        with col2:
            col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

        with col3:
            st.session_state["fighter_2"] = col3.selectbox("Combattant 2", options)
            fighter_2 = st.session_state["fighter_2"]
            if fighter_2 != "None":
                st.session_state["url_2"] = df.loc[
                    df["name"] == fighter_2, "img_cbt"
                ].iloc[0]
                if st.session_state["url_2"] == "NO":  # type: ignore
                    st.session_state["url_2"] = os.path.join(
                        "FightPredixApp\img", "fighter.png"
                    )

                col3.image(st.session_state["url_2"], width=300)

        if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
            titre("Choisissez deux combattants différents.")
            st.session_state["predictable"] = False
        else:
            with col2:
                if col2.button("", key="predict"):
                    st.session_state["predictable"] = True

        with a2:

            df_filtre = df[
                [
                    "name",
                    "précision_saisissante",
                    "précision_de_takedown",
                    "sig_str_défense",
                    "défense_de_démolition",
                ]
            ]

            df_filtre.rename(
                columns={
                    "précision_saisissante": "strike acccuracy",
                    "précision_de_takedown": "takedown accuracy",
                    "sig_str_défense": "strike defense",
                    "défense_de_démolition": " takedown defense",
                }
            )

            categories = [
                "strike acccuracy",
                "takedown accuracy",
                "strike defense",
                " takedown defense",
            ]

            fig_1 = go.Figure()
            for name in [fighter_1, fighter_2]:
                if name != "None":
                    person_data = (
                        df_filtre[df_filtre["name"] == name].iloc[0, 1:].tolist()
                    )
                else:
                    person_data = [0, 0, 0, 0]
                fig_1.add_trace(
                    go.Scatterpolar(
                        r=person_data,
                        theta=categories + [categories[0]],
                        fill="toself",
                        name=name,
                    )
                )

            fig_1.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                height=500,
                width=700,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        x=1.20,
                        y=0,
                        xref="paper",
                        yref="paper",
                        text="strike accuracy: Le pourcentage de coups réussis.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    ),
                    dict(
                        x=1.20,
                        y=-0.05,
                        xref="paper",
                        yref="paper",
                        text="takedown accuracy: Le pourcentage de takedown réussies.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    ),
                    dict(
                        x=1.20,
                        y=-0.10,
                        xref="paper",
                        yref="paper",
                        text="strike defense: Le pourcentage de coups bloqués.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    ),
                    dict(
                        x=1.20,
                        y=-0.15,
                        xref="paper",
                        yref="paper",
                        text="takedown defense: Le pourcentage de takedown bloqués.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    ),
                    dict(
                        x=0,
                        y=-0.2,
                        xref="paper",
                        yref="paper",
                        text="NB : Des données peuvent ne pas être disponibles.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    ),
                ],
            )

            fig_2 = go.Figure()

            for name in [fighter_1, fighter_2]:
                if name != "None":
                    person_data = (
                        df[(df["name"] == name)][
                            ["sig_str_head", "sig_str_body", "sig_str_leg"]
                        ]
                        .iloc[0]
                        .tolist()
                    )
                    fig_2.add_trace(
                        go.Bar(
                            x=["frappe tête", "frappe corp", "frappe jambes"],
                            y=person_data,
                            name=name,
                        )
                    )

            fig_2.update_layout(
                barmode="group",
                height=500,
                width=700,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                annotations=[
                    dict(
                        x=0.5,
                        y=-0.2,
                        xref="paper",
                        yref="paper",
                        text="NB : Des données peuvent ne pas être disponibles.",
                        showarrow=False,
                        font=dict(size=12),
                        align="center",
                    )
                ],
            )

            e1, e2 = st.columns([1, 1])

            with e1:
                st.plotly_chart(fig_1, use_container_width=True)

            with e2:
                st.plotly_chart(fig_2, use_container_width=True)

            if "portee_de_la_jambe" in df.columns or "age" in df.columns:
                df.rename(
                    columns={"portee_de_la_jambe": "portée_de_la_jambe", "age": "âge"},
                    inplace=True,
                )
            data = df.loc[
                (df["name"] == fighter_1) | (df["name"] == fighter_2),
                [
                    "name",
                    "poids",
                    "âge",
                    "win",
                    "losses",
                    "draws",
                    "ko_tko",
                    "sub",
                    "dec",
                ],
            ]  # "LA TAILLE"
            data.set_index("name", inplace=True)
            data = data.round(1)
            st.table(data.style.format("{:.0f}"))

elif st.session_state.current_page == "predictions":
    # page_predictions()
    if st.session_state["predictable"] == False:
        titre("Choisissez deux combattants différents.")
    else:
        if "DataFighters" in st.session_state and "DataCombats" in st.session_state:
            DataFighters = st.session_state["DataFighters"]
            DataCombats = st.session_state["DataCombats"]

            num_features, cat_features, output_features = _liste_features()

            predictions: list = []

            if (
                "portée_de_la_jambe" in DataFighters.columns
                or "âge" in DataFighters.columns
            ):
                DataFighters.rename(
                    columns={"portée_de_la_jambe": "portee_de_la_jambe", "âge": "age"},
                    inplace=True,
                )

            indice_nom1 = DataFighters[
                DataFighters["name"] == st.session_state["fighter_1"]
            ].index[0]
            indice_nom2 = DataFighters[
                DataFighters["name"] == st.session_state["fighter_2"]
            ].index[0]

            resultats = _prediction_streamlit(
                indice_nom1,
                indice_nom2,
                DataFighters,
                num_features,
                cat_features,
            )

            if st.session_state["url_1"][19:26] != "fighter":
                image_path_1 = _download_et_convert_image(
                    st.session_state.get("url_1", "None"), "FightPredixApp/img/cbt1.jpg"
                )
            else:
                image_path_1 = st.session_state["url_1"]

            if st.session_state["url_2"][19:26] != "fighter":
                image_path_2 = _download_et_convert_image(
                    st.session_state.get("url_2", "None"), "FightPredixApp/img/cbt2.jpg"
                )
            else:
                image_path_2 = st.session_state["url_2"]

            if image_path_1 is not None and image_path_2 is not None:
                cbt1 = Image.open(image_path_1)
                cbt2 = Image.open(image_path_2)

            values = [resultats[0], resultats[1]]
            labels = [st.session_state["fighter_1"], st.session_state["fighter_2"]]
            imgs = [cbt1, cbt2]

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=labels, y=values, marker_color=["#00172B", "#00172B"], opacity=1
                )
            )

            fig.add_layout_image(
                dict(
                    source=cbt1,
                    xref="x domain",
                    yref="y domain",
                    x=0.75 - 1 / 2,
                    y=values[0] / 2,
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
                    y=values[1] / 2,
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
                    title=" ", range=[0, 2], showticklabels=False, showgrid=False
                ),
                height=600,
                width=900,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                template="plotly_white",
            )

            _, cent_co, _ = st.columns([1, 1, 1])
            with cent_co:
                st.plotly_chart(fig)
                st.write(
                    f"Selon l'algorrithme, {st.session_state['fighter_1']} a une probabilité de vaincre {st.session_state['fighter_2']} de {round(values[0] * 100)}%, la où {st.session_state['fighter_2']} a une probabilité de vaincre {st.session_state['fighter_1']} de {round(values[1] * 100)}%."
                )
