import streamlit as st
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
        if st.button("🏠 Accueil", key="home"):
            st.session_state.current_page = "home"
    with col5:
        if st.button("📧 Contact", key="contact"):
            st.session_state.current_page = "contact"

    with col3:
        if st.button("🥊 Combattants", key="combattants"):
            st.session_state.current_page = "combattants"

    with col4:
        if st.button("📊 Prédictions", key="predictions"):
            st.session_state.current_page = "predictions"

navbar()

def navbar_sidebar():

    st.sidebar.title("Navigation")
    col1, col2, col3, col4 = st.sidebar.columns(4, gap="small")

    with col1:
        if st.sidebar.button("🏠 Accueil", key="home_sidebar"):
            st.session_state.current_page = "home"

    with col2:
        if st.sidebar.button("🥊 Combattants", key="combattants_sidebar"):
            st.session_state.current_page = "combattants"

    with col3:
        if st.sidebar.button("📊 Prédictions", key="predictions_sidebar"):
            st.session_state.current_page = "predictions"

    with col4:
        if st.sidebar.button("📧 Contact", key="contact_sidebar"):
            st.session_state.current_page = "contact"


navbar_sidebar()


if st.session_state.current_page == "home":
    st.title("Bienvenue sur FightPredix !")
    st.write("Ceci est la page d'accueil.")

elif st.session_state.current_page == "combattants":
    st.title("Section Combattants")
    st.write("Ici, vous verrez les combattants...")

elif st.session_state.current_page == "predictions":
    st.title("Section Prédictions")
    page_predictions()

else:
    st.title("Page non trouvée")
    st.write("La page demandée n'existe pas.")
