from dotenv import load_dotenv
import snowflake.connector
import os


def load_connection() -> snowflake.connector.cursor.SnowflakeCursor:
    """
    Function to generate snowflake connection
    """

    # Load environment variables and create snowflake connection
    load_dotenv()
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_HOST"),
        user=os.getenv("SNOWFLAKE_USERNAME"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        port=443,
        protocol='https'
    )

    # Create a cursor object.
    cur = conn.cursor()
    cur.execute(f"""USE WAREHOUSE {os.getenv("SNOWFLAKE_WAREHOUSE")}""")
    cur.execute(f"""USE ROLE {os.getenv("SNOWFLAKE_ROLE")}""")

    return cur
