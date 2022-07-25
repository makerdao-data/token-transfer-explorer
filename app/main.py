import streamlit as st
from src.config.conn_init import load_connection
from src.multipage import MakerView
from src.pages import landing
from src.pages import transfers
from src.pages import balances

# Set wide visual feed
st.set_page_config(page_title="MakerDAO Token Transfer Explorer", layout="wide") 
st.title("MakerDAO Token Transfer Explorer")

if 'cur' not in st.session_state:
    st.session_state.cur = load_connection()
if st.session_state.cur.is_closed():
    st.session_state.cur = load_connection()

# Initializing app class
app = MakerView()

# Adding app pages
app.add_page("Landing Page", landing.app)
app.add_page("Token Transfers", transfers.app)
app.add_page("Token Balances", balances.app)

# Run application
try:
    app.run()
except ValueError:
    pass