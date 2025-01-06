import streamlit as st
import base64


# Fonction pour convertir une image en Base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Charger l'image et l'injecter dans le CSS
def custom_global(image_file):
    base64_image = get_base64_of_bin_file(image_file)
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Bangers&display=swap');


        .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("data:image/png;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        """,
        unsafe_allow_html=True,
    )


def get_audio_base64(audio_file):
    with open(audio_file, "rb") as f:
        data = f.read()
    return f"data:audio/mpeg;base64,{base64.b64encode(data).decode()}"


def custom_navbar():
    st.markdown(
        f"""
        <style>
        /* Masquer la barre supérieure par défaut de Streamlit */

        .stAppHeader {{
            z-index: -1;
            width: 100%;
            height: 85px;
            color: white;
            font-family: 'Bangers', sans-serif;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            animation: fadeInBackground 1.5s ease-in-out forwards; /* Animation à déclencher */
            animation-delay: 0.5s;
        }}

        #stDecoration {{
            background-image: none;
            z-index: -1;
        }}

        /* Déplacer le contenu principal de Streamlit pour qu'il ne chevauche pas la navbar */
        .stApp {{
            margin-top: 85px; /* Hauteur de la navbar */
        }}

        .st-emotion-cache-5dda5n {{
            display: None; /* Masquer la barre supérieure par défaut de Streamlit */
        }}

        /* logo en haut à gauche */
        div.stHorizontalBlock:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)
        {{
            border: None;
            z-index: 1;
            color: red; /* Couleur du texte */
            transition: 0.5s;
        }}

        div.stHorizontalBlock:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) img{{
            transition: 0.5s; /* Transition pour l'effet de zoom */
            height: 85px; /* Taille de l'image */
            animation: hitNavbar 1.5s;
        }}

        div.stHorizontalBlock:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) img:hover {{
            transform: scale(1.3); /* Agrandir légèrement l'image au survol */
            cursor: pointer; /* Changer le curseur au survol */
        }}

        div.stHorizontalBlock:nth-child(3) {{
            top: 0;
            left: 0;
            width: 15%;
            height: 85px;
            background-color: transparent;
            position: fixed;
            align-items: center;
        }}

        div.stHorizontalBlock:nth-child(4) {{
            top: 0;
            left: 15%;
            width: 70%;
            gap: 20px;
            height: 85px;
            background-color: transparent;
            position: fixed;
            align-items: center;
        }}


        /* Boutons de la navbar */
        .st-key-home > div:nth-child(1) > button:nth-child(1),
        .st-key-combattants > div:nth-child(1) > button:nth-child(1),
        .st-key-predictions > div:nth-child(1) > button:nth-child(1),
        .st-key-contact > div:nth-child(1) > button:nth-child(1) {{
            border: None; /* Supprimer la bordure */
            color: white; /* Couleur du texte */
            background-image: linear-gradient(rgba(255, 0, 0, 0.8), rgba(0, 0, 0, 1)); /* Dégradé de couleur */
            width: 130px; /* Largeur */
            box-shadow: 0 0 10px red; /* Ombre portée */
            transition: 1s, z-index 0s; /* Transition */
            animation: hitNavbar 1.5s; /* Animation */
        }}


        .st-key-home > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        .st-key-combattants > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        .st-key-predictions > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        .st-key-contact > div:nth-child(1) > button:nth-child(1) > div:nth-child(1){{
            background-color: #00172B;
            border: None;
            padding: 5px 2px; /* Espacement */
            font-family: 'Bangers', sans-serif;
            transition: 1s, z-index 0s;
            background-color: transparent;
        }}

        .st-key-home > div:nth-child(1) > button:nth-child(1):hover,
        .st-key-combattants > div:nth-child(1) > button:nth-child(1):hover,
        .st-key-predictions > div:nth-child(1) > button:nth-child(1):hover,
        .st-key-contact > div:nth-child(1) > button:nth-child(1):hover {{
            transform: scale(1.2); /* Agrandir légèrement le bouton au survol */
        }}

        .st-key-home > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        .st-key-combattants > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        .st-key-predictions > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        .st-key-contact > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover{{
            color: red;
            cursor: pointer;
            z-index: 1;
        }}


        div.st-emotion-cache-aajpza:nth-child(2),
        div.st-emotion-cache-aajpza:nth-child(3),
        div.st-emotion-cache-aajpza:nth-child(4),
        div.st-emotion-cache-aajpza:nth-child(5){{
            margin-left : -300px
        }}


        /* élément de la sidebar */
        .st-emotion-cache-hzo1qh > img:nth-child(1), .st-emotion-cache-79elbk, .st-emotion-cache-kgpedg > img:nth-child(1){{
            display: None;
        }}

        .stSidebar {{
            width: 10px !important;
            display: None;
        }}

        div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1){{
            border: None;
            font-family: 'Bangers', sans-serif;
            transition: 1s, z-index 0s;
            background-image: linear-gradient(rgba(255, 0, 0, 0.8), rgba(0, 0, 0, 1));
            width: 150px;
            border-radius: 5px;
            padding: 35px 10px;
            box-shadow: 0 0 10px red;
        }}

        div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover{{
            color: red;
            transform: scale(1.2);
            cursor: pointer;
        }}

        div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1),
        div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1),
        div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1),
        div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1){{
            border: None;
            background-color: transparent;
        }}

        div.st-emotion-cache-5dda5n.e1dbuyne15 button.st-emotion-cache-1soyyad.e1obcldf18 {{
            background-image: linear-gradient(rgba(255, 0, 0, 0.6), rgba(0, 0, 0, 1)) !important;
        }}

        /*media query*/

        @media (max-width: 820px) {{
            div.stHorizontalBlock:nth-child(4) {{
                display: none;
            }}

            .stSidebar {{
                display: block;
            }}

            .stAppHeader {{
                background-image: url("data:image/png;base64,{get_base64_of_bin_file('./img/fissurenav.png')}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                height: 85px;
            }}

            div.st-emotion-cache-5dda5n.e1dbuyne15 {{
                display: block;
                margin-top: 80px;
            }}




        }}
        @media (max-width: 1000px) {{
            div.stHorizontalBlock:nth-child(4) p {{
                font-size: 14px;
            }}
        }}

        @keyframes hitNavbar {{
                0% {{
                    opacity: 0; /* Complètement transparent */
                    transform: translateY(-50px) scale(0.5); /* En dehors de l'écran, plus petit */
                }}
                50% {{
                    opacity: 1; /* Devient visible */
                    transform: translateY(20px) scale(1.4); /* "Frappe" la navbar */
                }}
                70% {{
                    transform: translateY(0px) scale(0.95); /* Rebond légèrement */
                }}
                100% {{
                    transform: translateY(0px) scale(1); /* Position finale stable */
                }}
            }}


        @keyframes fadeInBackground {{
            0% {{
                background-image: none; /* Transparent au début */
            }}
            100% {{
                background-image: url("data:image/png;base64,{get_base64_of_bin_file('./img/fissurenav.png')}"); /* Image de fond */
            }}
        }}

    """,
        unsafe_allow_html=True,
    )


def init_pages():
    st.set_page_config(
        page_title="FightPredix",
        page_icon="🥊",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    custom_navbar()

    custom_global("img/fissure.png")
