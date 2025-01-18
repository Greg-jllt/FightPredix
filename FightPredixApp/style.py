import streamlit as st
import os
import sys
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Fonction pour convertir une image en Base64
def get_base64_of_bin_file(bin_file):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, bin_file)
    with open(full_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# , url("data:image/png;base64,{base64_image}")
# Charger l'image et l'injecter dans le CSS
def custom_global():
    # base64_image = get_base64_of_bin_file(image_file)
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Bangers&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Pirata+One&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=IM+Fell+Great+Primer+SC&family=Pirata+One&display=swap');

        .stApp {
            background: linear-gradient(rgba(160, 0, 0, 0.8), rgba(0, 23, 43, 0.8));
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }

        p {
            font-family: "IM Fell Great Primer SC", serif;
        }
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
            font-family: "Pirata One", serif;
            # font-family: 'Bangers', sans-serif;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            # background: linear-gradient(rgba(0, 23, 43, 0.8), rgba(160, 0, 0, 0.8));
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
            left: 25%;
            width: 70%;
            gap: 20px;
            height: 85px;
            background-color: transparent;
            position: fixed;
            align-items: center;
        }}

        /* Bouton predict */

        .st-key-predict > div:nth-child(1) > button:nth-child(1) {{
            background-image: linear-gradient(rgba(0, 23, 43, 1), rgba(0, 23, 43, 1));
            display: flex;
            align-items: center; 
            justify-content: center;
            gap: 0px; /* Espacement entre l'image et le texte */
            padding: 5px 0px; /* Espacement interne en fonction de la largeur de l'écran */
            height: 55 px; /* Ajuste automatiquement la hauteur en fonction du contenu */
            min-width:100%;
            position: relative;
        }}

        .st-key-predict > div:nth-child(1) > button:nth-child(1)::before {{
            content: "";
            display: inline-block;
            width: 2.5vw; /* Largeur de l'image relative à la largeur du bouton */
            height: 2vw; /* Ajuste la hauteur automatiquement pour garder les proportions */
            background-image: url("data:image/png;base64,{get_base64_of_bin_file('./img/logo.png')}");
            background-size: contain; 
            background-repeat: no-repeat; 
        }}

        /* Media query pour les petits écrans */
        @media (max-width: 768px) {{
            .st-key-predict > div:nth-child(1) > button:nth-child(1) {{
                padding: 2vw 3vw; /* Augmente l'espacement sur les petits écrans */
                min-height: 45px; /* Réduit légèrement la hauteur minimale */
            }}

            .st-key-predict > div:nth-child(1) > button:nth-child(1)::before {{
                width: 15%; /* Ajuste l'image pour qu'elle soit plus petite sur les petits écrans */
                max-width: 40px; /* Réduit la limite maximale pour l'image */
            }}
        }}



        /* Boutons de la navbar */
        .st-key-home > div:nth-child(1) > button:nth-child(1),
        .st-key-combattants > div:nth-child(1) > button:nth-child(1),
        .st-key-predictions > div:nth-child(1) > button:nth-child(1),
        .st-key-contact > div:nth-child(1) > button:nth-child(1) {{
            border: None; /* Supprimer la bordure */
            color: white; /* Couleur du texte */
            background-image: linear-gradient(rgba(160, 0, 0, 0.8), rgba(160, 0, 0, 0.8)); /* Dégradé de couleur */
            width: 130px; /* Largeur */
            # box-shadow: 0 0 10px red; /* Ombre portée */
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
            font-family: "Pirata One", serif;
            # font-family: 'Bangers', sans-serif;
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
        # .st-emotion-cache-hzo1qh > img:nth-child(1), .st-emotion-cache-79elbk, .st-emotion-cache-kgpedg > img:nth-child(1){{
        #     display: None;
        # }}

        # .stSidebar {{
        #     width: 10px !important;
        #     display: None;
        # }}

        # div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        # div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        # div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1),
        # div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1){{
        #     border: None;
        #     font-family: "Pirata One", serif;
        #     # font-family: 'Bangers', sans-serif;
        #     transition: 1s, z-index 0s;
        #     background-image: linear-gradient(rgba(100, 0, 0, 0.8), rgba(0, 0, 0, 1));
        #     width: 150px;
        #     border-radius: 5px;
        #     padding: 35px 10px;
        #     box-shadow: 0 0 10px red;
        # }}

        # div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        # div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        # div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover,
        # div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1) > div:nth-child(1):hover{{
        #     color: red;
        #     transform: scale(1.2);
        #     cursor: pointer;
        # }}

        # div.stElementContainer:nth-child(3) > div:nth-child(1) > button:nth-child(1),
        # div.stElementContainer:nth-child(4) > div:nth-child(1) > button:nth-child(1),
        # div.stElementContainer:nth-child(5) > div:nth-child(1) > button:nth-child(1),
        # div.stElementContainer:nth-child(6) > div:nth-child(1) > button:nth-child(1){{
        #     border: None;
        #     background-color: transparent;
        # }}

        # div.st-emotion-cache-5dda5n.e1dbuyne15 button.st-emotion-cache-1soyyad.e1obcldf18 {{
        #     background-image: linear-gradient(rgba(100, 0, 0, 0.6), rgba(0, 0, 0, 1)) !important;
        # }}

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


        # @keyframes fadeInBackground {{
        #     0% {{
        #         background-image: none; /* Transparent au début */
        #     }}
        #     100% {{
        #         background-image: url("data:image/png;base64,{get_base64_of_bin_file('./img/fissurenav.png')}"); /* Image de fond */
        #     }}
        # }}

    """,
        unsafe_allow_html=True,
    )


# def fleche_menu():
#     st.markdown(
#         f"""
#     <style>
#     [data-testid="stSidebarNav"] svg {{
#         display: none !important;
#     }}
#     </style>
# """, unsafe_allow_html=True)


def bouton_prediction():
    def get_base64_image(chemin):
        with open(chemin, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    image_base64 = get_base64_image("img/logo.png")

    st.markdown(f"""
    <style>
    .custom-button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 20px;
        color: white;
        background-color: #00172B;
        border: none;
        border-radius: 7px;
        cursor: pointer;
        text-decoration: none;
        width: 80 px;
        height: 50px;
    }}
    .custom-button img {{
        width: 80px;
        height: 40px;
        margin-right: 0px;
    }}
    </style>
    <a class="custom-button" onclick="document.location.reload()">
        <img src="data:image/png;base64,{image_base64}" alt="Icon">
    </a>
    """, unsafe_allow_html=True)


def init_pages():
    st.set_page_config(
        page_title="FightPredix",
        page_icon="🥊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # fleche_menu()

    custom_navbar()

    custom_global()