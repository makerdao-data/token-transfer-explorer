import streamlit as st
import pandas as pd
from ..utils.tokens.tkn_bal_txn_display import tkn_bal_txn_display


def app():
    """
    Token Balance Explorer
    """

    # Display page title
    st.title("Token Balance Explorer")

    # Prompt inputs and generate query parameters
    query_params = tkn_bal_txn_display('bal')

    # If query parameters were generated...
    if query_params:

        holders_query = f"""
            select count(distinct address)
            from maker.balances.{query_params[1]}
            where date >= '{query_params[2][0]}' and date <= '{query_params[2][1]}';
        """

        @st.experimental_memo(ttl=600)
        def fetch_holders(holders_query):
            return st.session_state.cur.execute(holders_query).fetchone()[0]

        # Display result KPIs
        with st.expander("Result KPIs", expanded=True):
            with st.container():
                # Display metrics within container
                # st.metric(label="Unique holders", value='{:,}'.format(len(df.ADDRESS.unique())))
                st.metric(label="Unique holders", value='{:,}'.format(fetch_holders(holders_query)))

        top_50_query = f"""
            select address, balance
            from maker.balances.{query_params[1]}
            where date = (select max(date) from maker.balances.{query_params[1]} where date <= '{query_params[2][1]}')
            order by balance desc
            limit 50;
        """
        @st.experimental_memo(ttl=600)
        def fetch_top_holders(top_50_query):
            return st.session_state.cur.execute(top_50_query).fetchall()

        # Display result table visualizations
        with st.expander("Result Tables", expanded=True):
            with st.container():
                # Display dataframe tables within container
                st.markdown(f"Top 50 {query_params[1]} holders")
                # st.dataframe(df.sort_values(by='DATE').drop_duplicates('ADDRESS', keep='last').nlargest(50, 'BALANCE').reset_index(drop=True))
                st.dataframe(
                    pd.DataFrame(
                        fetch_top_holders(top_50_query),
                        columns=['Address', 'Balance']
                    )
                )