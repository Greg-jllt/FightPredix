import streamlit as st
import pandas as pd
import base64
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

file_path = os.path.join("data","Data_ufc_fighters_t1.csv")

if os.path.exists(file_path):

    df = pd.read_csv(file_path)

    division = st.selectbox("Choose a category", list(df["Division"].unique()))

    df = df[df["Division"] == division]

    col1, col2, col3 = st.columns([1.5, 0.5, 1.5])

    options = list(df["Name"])
    options.insert(0, "None")

    with col1:
        fighter_1 = st.selectbox("Choose fighter 1", options)
        if fighter_1 != "None":
            url = df.loc[df['Name'] == fighter_1, 'img_cbt'].iloc[0]
            if url == "NO":
                url = os.path.join("img", "fighter.png")
            col1.image(url, width=300)

    with col2:
        col2.markdown('<div class="vs-text">VS</div>', unsafe_allow_html=True)

    with col3:
        fighter_2 = col3.selectbox("Choose fighter 2", options)
        if fighter_2 != "None":
            url = df.loc[df['Name'] == fighter_2, 'img_cbt'].iloc[0]
            col3.image(url, width=300)

    if fighter_1 == "None" or fighter_2 == "None" or fighter_1 == fighter_2:
        st.write("## Please select two different fighters.")
    else: 
        data = df.loc[(df["Name"] == fighter_1) | (df["Name"] == fighter_2), ["Name", "Poids","La Taille", "Âge","Win","Losses", "Draws", "KO/TKO", "SUB", "DEC"]]
        data.set_index("Name", inplace=True)
        data = data.round(1)
        st.table(data.style.format("{:.0f}"))
        _, c1, _ = st.columns([1.5, 0.5, 1.5], vertical_alignment="center")
        c1.button("Predict")
