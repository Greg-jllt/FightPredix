import streamlit as st
import pandas as pd
import base64
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import os 
import numpy as np

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

left_co, cent_co,last_co = st.columns([1, 3, 1])
with cent_co:
    st.image(os.path.join("img", "logo.png"), width=350)

file_path = os.path.join("data/Data_ufc_fighters.csv")

if os.path.exists(file_path):

    df = pd.read_csv(file_path)

    division = st.selectbox("Choose a category", list(df["DIVISION"].unique()))

    df = df[df["DIVISION"] == division]

    col1, col2, col3 = st.columns([1.5, 0.5, 1.5])

    options = list(df["NAME"])
    options.insert(0, "None")

    with col1:
        fighter_1 = st.selectbox("Choose fighter 1", options)
        if fighter_1 != "None":
            url = df.loc[df['NAME'] == fighter_1, 'img_cbt'].iloc[0]
            if url == "NO":
                url = os.path.join("img", "fighter.png")
            col1.image(url, width=300)

    with col2:
        col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

    with col3:
        fighter_2 = col3.selectbox("Choose fighter 2", options)
        if fighter_2 != "None":
            url = df.loc[df['NAME'] == fighter_2, 'img_cbt'].iloc[0]
            if url == "NO":
                url = os.path.join("img", "fighter.png")
            col3.image(url, width=300)

    if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
        st.write("## Please select two different fighters.")
    else: 
        data = df.loc[(df["NAME"] == fighter_1) | (df["NAME"] == fighter_2), ["NAME", "POIDS", "ÂGE","WIN","LOSSES", "DRAWS", "KO/TKO", "SUB", "DEC"]] #"LA TAILLE"
        data.set_index("NAME", inplace=True)
        data = data.round(1)
        st.table(data.style.format("{:.0f}"))

        df_filtre = df[["NAME",'PRÉCISION SAISISSANTE','PRÉCISION DE TAKEDOWN','SIG. STR.DÉFENSE','DÉFENSE DE DÉMOLITION']]

        df_filtre.rename(columns={
            'PRÉCISION SAISISSANTE': 'strike acccuracy',
            'PRÉCISION DE TAKEDOWN': 'takedown accuracy',
            'SIG. STR.DÉFENSE': 'strike defense',
            'DÉFENSE DE DÉMOLITION': ' takedown defense'
        })

        categories =['strike acccuracy', 'takedown accuracy', 'strike defense', ' takedown defense']

        fig = go.Figure()

        for name in [fighter_1, fighter_2]:
            person_data = df_filtre[df_filtre['NAME'] == name].iloc[0, 1:].tolist()
            fig.add_trace(go.Scatterpolar(
                r=person_data,
                theta=categories + [categories[0]],
                fill='toself',
                name=name
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)


        _, c1, _ = st.columns([1.5, 0.5, 1.5], vertical_alignment="center")
        c1.button("Predict")

