import streamlit as st

st.set_page_config(
    page_title="FightPredix", page_icon="🥊", initial_sidebar_state="expanded"
)

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
