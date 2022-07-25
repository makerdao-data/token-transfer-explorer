import streamlit as st
import pandas as pd
import snowflake.connector
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from ...config.sf import SNOWFLAKE_HOST, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_USERNAME, SNOWFLAKE_WAREHOUSE

def tkn_bal_txn_display(topic: str) -> tuple: 
    """
    Function to display token balances/transaction details

    Params:
        topic (str): Topic of query. Currently 'bal' or 'txs.'
    """

    # Select token
    token = st.selectbox(
        "Select a token", 
        ('', 'MKR', 'DAI'),
         format_func=lambda x: 'Select an option' if x == '' else x
    )

    @st.experimental_singleton
    def init_connection():
        print()
        print('Initializing DB connection...')
        print()
        return snowflake.connector.connect(
            account=SNOWFLAKE_HOST,
            user=SNOWFLAKE_USERNAME,
            password=SNOWFLAKE_PASSWORD,
            warehouse=SNOWFLAKE_WAREHOUSE,
            role=SNOWFLAKE_ROLE,
            port=443,
            protocol='https'
        )

    engine = init_connection()

    # Once token is selected...
    if token:
        with st.expander("Query parameters", expanded=True):
            # Negate block indexing for balance explorations
            if topic != 'bal':
                opts = ('Date', 'Block')
            else:
                opts = ['Date']

            # Select query index/filter parameters
            indexer = st.selectbox('Index by:', opts)

            # If 'Date' is selected...
            if indexer == 'Date':

                # Min date selection
                if token == 'DAI':

                    min_max_date_query = f"""
                        SELECT min(date(timestamp)), max(date(timestamp))
                        FROM maker.transfers.{token};
                    """
                    @st.experimental_memo(ttl=600)
                    def fetch_min_max_date(min_max_date_query):
                        return engine.cursor().execute(min_max_date_query).fetchone()

                    values_range = fetch_min_max_date(min_max_date_query)
                    min_value = values_range[1] - timedelta(days=30)
                    max_delta = 30

                elif token == 'MKR':

                    min_max_date_query = f"""
                        SELECT min(date(timestamp)), max(date(timestamp))
                        FROM maker.transfers.{token};
                    """
                    @st.experimental_memo(ttl=600)
                    def fetch_min_max_date(min_max_date_query):
                        return engine.cursor().execute(min_max_date_query).fetchone()

                    values_range = fetch_min_max_date(min_max_date_query)
                    min_value = values_range[1] - timedelta(days=30)
                    max_delta = 30

                # Date input with date range
                date_input = st.date_input(
                    f'Select date range ({max_delta} day maximum):',
                    value=(
                        (min_value, values_range[1])
                    ),
                    max_value=values_range[1],
                    min_value=values_range[0]
                )
                
                # Query conditionals
                if len(date_input) == 2:
                    if (date_input[1] - date_input[0]) <= timedelta(days=max_delta):
                        if st.button('Query'):
                            # Return tuple of selected token and date parameters
                            return (topic, token, date_input)

            # If 'Block' is selected...
            if indexer == 'Block':

                min_max_block_query = f"""
                    SELECT min(block), max(block)
                    FROM maker.transfers.{token};
                """
                @st.experimental_memo(ttl=600)
                def fetch_max_block(max_block_query):
                    return engine.cursor().execute(max_block_query).fetchone()
                
                values_range = fetch_max_block(min_max_block_query)

                # Block inputs
                st.write("Maximum block range: 150,000.")
                start_block_input = st.number_input(
                    'Select start block:',
                    value = values_range[1] - 150000,
                    min_value = values_range[0],
                    max_value = values_range[1] 
                )
                end_block_input = st.number_input(
                    'Select end block:',
                    value = values_range[1],
                    min_value = values_range[0],
                    max_value = values_range[1]
                )

                # Query conditionals
                if start_block_input < end_block_input:
                    if (end_block_input - start_block_input) <= 150000:
                        if st.button('Query'):
                            # Return tuple of selected token and block parameters
                            return (topic, token, (start_block_input, end_block_input))
