import streamlit as st
import pandas as pd
import snowflake.connector
from ..utils.tokens.tkn_bal_txn_display import tkn_bal_txn_display
from ..config.sf import SNOWFLAKE_HOST, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_USERNAME, SNOWFLAKE_WAREHOUSE


def app():
    """
    Token Transfer Explorer
    """

    # Display page title
    st.title("Token Transfer Explorer")
    
    # Prompt inputs and generate query parameters
    query_params = tkn_bal_txn_display('txs')

    # If query parameters were generated...
    if query_params:

        # Generate analysis metrics

        if type(query_params[2][0]) == int:
            cond = 'block'
            c0 = query_params[2][0]
            c1 = query_params[2][1]
        else:
            cond = 'timestamp'
            c0 = query_params[2][0].__str__()[:10] + ' 00:00:00'
            c1 = query_params[2][1].__str__()[:10] + ' 23:59:59'

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
        
        ttq_query = f"""
            SELECT count(*)
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}';
        """
        @st.experimental_memo(ttl=600)
        def fetch_ttq(ttq_query):
            return engine.cursor().execute(ttq_query).fetchone()[0]

        adtq_query = f"""
            select avg(sum_transfers)
            from (SELECT date(timestamp), count(*) sum_transfers
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}'
            group by date(timestamp));
        """
        @st.experimental_memo(ttl=600)
        def fetch_adtq(adtq_query):
            return engine.cursor().execute(adtq_query).fetchone()[0]

        ttv_query = f"""
            SELECT sum(amount)
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}';
        """
        @st.experimental_memo(ttl=600)
        def fetch_ttv(ttv_query):
            return engine.cursor().execute(ttv_query).fetchone()[0]

        adtv_query = f"""
            select avg(sum_amount)
            from (SELECT date(timestamp), sum(amount) sum_amount
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}'
            group by date(timestamp));
        """
        @st.experimental_memo(ttl=600)
        def fetch_adtv(adtv_query):
            return engine.cursor().execute(adtv_query).fetchone()[0]

        tv_query = f"""
            select timestamp, amount
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}'
            order by timestamp;
        """
        @st.experimental_memo(ttl=600)
        def fetch_tv(tv_query):
            return engine.cursor().execute(tv_query).fetchall()

        tq_query = f"""
            select timestamp, count(*)
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}'
            group by timestamp
            order by timestamp;
        """
        @st.experimental_memo(ttl=600)
        def fetch_tq(tq_query):
            return engine.cursor().execute(tq_query).fetchall()

        top_10_query = f"""
            select timestamp, block, tx_hash, sender, receiver, amount
            FROM maker.transfers.{query_params[1]}
            where {cond} >= '{c0}'
            and {cond} <= '{c1}'
            order by amount desc
            limit 10;
        """
        @st.experimental_memo(ttl=600)
        def fetch_top_10(top_10_query):
            return engine.cursor().execute(top_10_query).fetchall()

        # Display result KPIs
        with st.expander("Result KPIs", expanded=True):
            # Display metrics in vertical columns
            with st.container():

                # Create columns
                quant_col1, quant_col2 = st.columns(2)

                with quant_col1:
                    st.metric(label="Total Transaction Quantity", value='{:,}'.format(fetch_ttq(ttq_query)))
                
                with quant_col2:
                    st.metric(label="Average Daily Transaction Quantity", value='{:,}'.format(round(fetch_adtq(adtq_query))))

            with st.container():
                vol_col1, vol_col2 = st.columns(2)

                with vol_col1:
                    st.metric(label=f"Total Transaction Volume (in {query_params[1]})", value='{:,}'.format(round(fetch_ttv(ttv_query), 2)))

                with vol_col2:
                    st.metric(label=f"Average Daily Transaction Volume (in {query_params[1]})", value='{:,}'.format(round(fetch_adtv(adtv_query), 2)))

        # Display result visualizations
        with st.expander("Result Visualizations", expanded=True):
            with st.container():
                # Display graph/chart visualizations wihin container
                st.markdown("Graph of daily transaction volume")

                def render_viz_1(tv_query):
                    st.bar_chart(
                        pd.DataFrame(
                            fetch_tv(tv_query), 
                            columns=['Date','Transaction Volume']).set_index('Date')
                    )
                
                render_viz_1(tv_query)

            with st.container():
                st.markdown("Graph of daily transaction quantity")
                def render_viz_2(tq_query):
                    st.bar_chart(
                        pd.DataFrame(
                            fetch_tq(tq_query), 
                            columns=['Date','Transaction Quantity']).set_index('Date')
                    )
                
                render_viz_2(tq_query)

        # Display table visualizations
        with st.expander("Result Tables", expanded=True):
            with st.container():
                # Display dataframe tables within container
                st.markdown(f"Top 10 Transfers by {query_params[1]}")
                st.dataframe(
                    pd.DataFrame(
                        fetch_top_10(top_10_query),
                        columns=['Timestamp', 'Block', 'Tx_hash', 'Sender', 'Receiver', 'Amount']
                    )
                )
