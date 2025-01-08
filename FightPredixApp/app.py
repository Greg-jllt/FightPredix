import base64
import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go


from pages import page_predictions
from style import init_pages

init_pages()

# Gestion de l'état pour suivre la page courante
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Page par défaut

# Navbar avec boutons Streamlit
def navbar():

    col1 = st.columns(1)[0]
    with col1:
        st.image("./img/logo_readme.png", width=100)

    col2, col3, col4, col5 = st.columns(4, gap="small")

    with col2:
        if st.button("Accueil", key="home"):
            st.session_state.current_page = "home"
    with col5:
        if st.button("Contact", key="contact"):
            st.session_state.current_page = "contact"

    with col3:
        if st.button("Combattants", key="combattants"):
            st.session_state.current_page = "combattants"

    with col4:
        if st.button("Prédictions", key="predictions"):
            st.session_state.current_page = "predictions"

navbar()

def navbar_sidebar():

    st.sidebar.title("Navigation")
    col1, col2, col3, col4 = st.sidebar.columns(4, gap="small")

    with col1:
        if st.sidebar.button("Accueil", key="home_sidebar"):
            st.session_state.current_page = "home"

    with col2:
        if st.sidebar.button("Combattants", key="combattants_sidebar"):
            st.session_state.current_page = "combattants"

    with col3:
        if st.sidebar.button("Prédictions", key="predictions_sidebar"):
            st.session_state.current_page = "predictions"

    with col4:
        if st.sidebar.button("Contact", key="contact_sidebar"):
            st.session_state.current_page = "contact"


def titre(texte):
    return st.markdown(
        f"""
        <p style="font-family:IM Fell Great Primer SC; font-size: 50px;">
        {texte}
        </p>
        """,
        unsafe_allow_html=True,
    )

navbar_sidebar()


if st.session_state.current_page == "home":
    titre("Bienvenue sur FightPredix !")
    st.write("Ceci est la page d'accueil.")


elif st.session_state.current_page == "combattants":
     
    _, cent_co,_ = st.columns([1.5,1, 1])

    with cent_co:
        titre("Section Combattants")
        st.write("Ici, vous verrez les combattants...")

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

    # with cent_co:
    #     st.image(os.path.join("img", "logo.png"), width=350)

    file_path = os.path.join("Data/Data_final_fighters.csv")

    a1,a2 = st.columns([0.5, 1])

    if os.path.exists(file_path):

        df = pd.read_csv(file_path)
 
        df = df.dropna(subset=["actif"])

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
                    url = df.loc[df['name'] == fighter_1, 'img_cbt'].iloc[0]
                    if url == "NO":
                        url = os.path.join("img", "fighter.png")
                    col1.image(url, width=300)

            with col2:
                col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

            with col3:
                st.session_state["fighter_2"] = col3.selectbox("Combattant 2", options)
                fighter_2 = st.session_state["fighter_2"]
                if fighter_2 != "None":
                    url = df.loc[df['name'] == fighter_2, 'img_cbt'].iloc[0]
                    if url == "NO":
                        url = os.path.join("img", "fighter.png")
                    col3.image(url, width=300)

            if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
                st.write("## Choisissez deux combattants différents.")

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
    titre("Section Prédictions")
    page_predictions()

    # def image_to_base64(image_path):
    #     with open(image_path, "rb") as image_file:
    #         encoded_string = base64.b64encode(image_file.read()).decode()
    #     return encoded_string

    # image_path = os.path.join("img", "test1.png")

    # image_base64 = image_to_base64(image_path)


    # # Générer la balise HTML pour afficher l'image avec base64
    # img_html = f'<img src="data:image/png;base64,{image_base64}" width="600">'

    # # Afficher l'image dans Streamlit via st.markdown 
    # st.markdown(img_html, unsafe_allow_html=True)

else:
    titre("Page non trouvée")
    st.write("La page demandée n'existe pas.")
