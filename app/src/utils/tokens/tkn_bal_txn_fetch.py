import pandas as pd
import streamlit as st
import pandas as pd
from datetime import date
from src.config.conn_init import load_connection


@st.experimental_memo(ttl=600)
def fetch_data(topic: str, token: str, params: tuple) -> pd.DataFrame:
    """
    Function to generate query and fetch results from query parameters

    Params:
        topic (str): Topic of query. Currently 'bal' or 'txs.'
        
        token (str): Token subject of query. Currently 'DAI' or 'MKR.'
        
        params (tuple): Query parameters. Date (datetime.date) or block (int).
    """

    if 'cur' not in st.session_state:
        st.session_state.cur = load_connection()
    if st.session_state.cur.is_closed():
        st.session_state.cur = load_connection()

    # Input assertions
    assert topic in ('txs', 'bal')
    assert token in ('MKR', 'DAI')
    assert type(params[0]) == type(params[1])
    assert type(params[0]) in (date, int)
    
    # Table selection
    if topic == 'txs':
        table = f'timestamp, block, tx_hash, sender, receiver, amount from maker.transfers.{token}'
    elif topic == 'bal':
        table = f'date, address, balance from maker.balances.{token}'

    # Conditional selection
    if type(params[0]) == date:
        #  Format date column string
        if 'transfers' in table:
            date_col = 'date(TIMESTAMP)'
        else:
            date_col = 'date'
        cond = f"where {date_col} >= '{params[0]}' and {date_col} <= '{params[1]}'"
    elif type(params[0]) == int:
        cond = f"where block >= {params[0]} and block <= {params[1]}"

    # Construct final query and fetch result
    try:
        print()
        print('Fetching data...')
        print()
        result = pd.read_sql(f"select {table} {cond}", engine)
    except Exception as e:
        print()
        print(f"""Fetching data failed. Error: {e}""")
        print('Reinitializing DB connection...')
        print()
        result = pd.read_sql(f"select {table} {cond}", st.session_state.cur)

    return result