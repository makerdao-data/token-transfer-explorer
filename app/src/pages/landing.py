import streamlit as st

def app():
    """
    Landing Page
    """
    
    # Page title and description
    st.title("Data Insights Core Unit presents:")
    st.header("Token Data Explorer")

    st.markdown("Welcome to the showcase of the newly created datasets for transfers and balances for DAI and MKR.")
    st.markdown("On the left hand sidebar, you can navigate to the transfers and balances sections.")

    st.markdown("The data is sourced from the Data Insights CU database. We will soon release the data through more channels, including API and Snowflake Marketplace. Feel free to contact us via [Discord](https://discord.gg/83YgvH2D) or the [Forum](https://forum.makerdao.com/).")
    # st.image('src/utils/images/screenshot.png') FileNotFound
