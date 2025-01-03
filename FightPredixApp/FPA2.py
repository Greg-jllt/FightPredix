import streamlit as st
import pandas as pd
import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import os

st.set_page_config(
    page_title="FightPredix",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# def image_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read()).decode()
#     return encoded_string

# image_path = os.path.join("img", "stade_mma.jpg")

# image_base64 = image_to_base64(image_path)

# st.markdown(
#     f"""
#     <style>
#         .stApp {{
#             background-image: url('data:image/jpeg;base64,{image_base64}');
#             background-size: 95% auto;
#             background-position: center center;
#             background-repeat: no-repeat;
#             height: 100vh;
#         }}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

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


_, cent_co,_ = st.columns([1.5,1, 1])

with cent_co:
    st.image(os.path.join("img", "logo.png"), width=350)

file_path = os.path.join("data/Data_ufc_fighters.csv")

a1,a2 = st.columns([0.5, 1])

if os.path.exists(file_path):

    df = pd.read_csv(file_path)

    df = df[df["Actif"] == True]

    with a1:

        division = st.selectbox("Catégorie", list(df["DIVISION"].unique()))

        df = df[df["DIVISION"] == division]

        col1, col2, col3 = st.columns([1.5, 0.5, 1.5])

        options = list(df["NAME"])
        options.insert(0, "None")

        with col1:
            st.session_state["fighter_1"] = st.selectbox("Combattant 1", options)
            fighter_1 = st.session_state["fighter_1"]
            if fighter_1 != "None":
                url = df.loc[df['NAME'] == fighter_1, 'img_cbt'].iloc[0]
                if url == "NO":
                    url = os.path.join("img", "fighter.png")
                col1.image(url, width=300)

        with col2:
            col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

        with col3:
            st.session_state["fighter_2"] = col3.selectbox("Combattant 2", options)
            fighter_2 = st.session_state["fighter_2"]
            if fighter_2 != "None":
                url = df.loc[df['NAME'] == fighter_2, 'img_cbt'].iloc[0]
                if url == "NO":
                    url = os.path.join("img", "fighter.png")
                col3.image(url, width=300)

        if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
            st.write("## Choisissez deux combattants différents.")

        with a2:

            df_filtre = df[["NAME",'PRÉCISION SAISISSANTE','PRÉCISION DE TAKEDOWN','SIG. STR.DÉFENSE','DÉFENSE DE DÉMOLITION']]

            df_filtre.rename(columns={
                'PRÉCISION SAISISSANTE': 'strike acccuracy',
                'PRÉCISION DE TAKEDOWN': 'takedown accuracy',
                'SIG. STR.DÉFENSE': 'strike defense',
                'DÉFENSE DE DÉMOLITION': ' takedown defense'
            })

            categories =['strike acccuracy', 'takedown accuracy', 'strike defense', ' takedown defense']

            fig_1 = go.Figure()
            for name in [fighter_1, fighter_2]:
                if name != "None":
                    person_data = df_filtre[df_filtre['NAME'] == name].iloc[0, 1:].tolist()
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
                    person_data = df[(df['NAME'] == name) ][["sig_str_head", "sig_str_body", "sig_str_leg"]].iloc[0].tolist()
                    fig_2.add_trace(go.Bar(
                        x=["frappe tête", "frappe corp", "frappe jambes"],
                        y=person_data,
                        name=name
                    ))

            fig_2.update_layout(
                barmode='group',
                height=500,
                width=700,
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

            data = df.loc[(df["NAME"] == fighter_1) | (df["NAME"] == fighter_2), ["NAME", "POIDS", "ÂGE","WIN","LOSSES", "DRAWS", "KO/TKO", "SUB", "DEC"]] #"LA TAILLE"
            data.set_index("NAME", inplace=True)
            data = data.round(1)
            st.table(data.style.format("{:.0f}"))
