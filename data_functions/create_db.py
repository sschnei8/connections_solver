#%%
import duckdb
from dotenv import load_dotenv
import os

def db_and_table():
    # Load environment variables from .env file
    load_dotenv()
    clean_csv_location = os.getenv('clean_csv')

    # Now that we have a clean CSV, we can read the csv from disk and write SQL against it using DuckDB
    # Create a DuckDB instance
    # duckdb.connect(dbname) creates a connection to a persistent database
    conn = duckdb.connect("connections.db")

    # Create DuckDB table
    conn.sql(
    """
    DROP TABLE IF EXISTS CONNECTIONS_DATA;
    CREATE TABLE CONNECTIONS_DATA (
        GAME_DATE DATE,
        DIFFICULTY VARCHAR,
        CATEGORY VARCHAR,
        WORD VARCHAR
    );
    """
    )

    # COPY CSV from disk
    conn.sql(
    f"""COPY CONNECTIONS_DATA FROM '{clean_csv_location}' (FORMAT CSV, HEADER);"""
    )

    # Clean up
    conn.close()

def clean_table():
    conn = duckdb.connect("connections.db")
    # Delete From Table Where SCRAPE/TRANSFORM Logic failed
    conn.execute(
    """
    -- GAMES WITH EXTRA ROWS CAUSED BY SPLITTING "-"
    WITH MESSED_UP_DATES_HYPHENS AS (
    SELECT GAME_DATE
         , CATEGORY
         , COUNT(1) / 4::FLOAT AS CNT -- BECASUE THERE WILL BE 4 ROWS FOR EACH INSTANCE
    FROM CONNECTIONS_DATA
    GROUP BY 1,2
    HAVING CNT % 1 <> 0
    ORDER BY CNT DESC
    ),

    -- GAMES WHERE CATEGORY WAS DUPLICATED AND DELETED BY BAD TRANSFORM LOGIC
    MESSED_UP_DATES_DUPES AS (
    SELECT GAME_DATE
         , COUNT(1) CNT
    FROM CONNECTIONS_DATA
    GROUP BY 1
    HAVING CNT % 16 <> 0
    )
    -- ALSO REMOVE APRIL FOOLS DAY EMOJI GAME
    DELETE FROM CONNECTIONS_DATA
    WHERE GAME_DATE IN (
        SELECT DISTINCT GAME_DATE FROM MESSED_UP_DATES_HYPHENS
        UNION ALL
        SELECT DISTINCT GAME_DATE FROM MESSED_UP_DATES_DUPES
        UNION ALL
        SELECT '2024-04-01'::DATE -- APRIL FOOLS DAY
        )
    """
    )
# %%
