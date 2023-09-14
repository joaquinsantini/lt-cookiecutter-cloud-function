import os
import json
import snowflake.connector
from logging import Logger
from snowflake.connector import SnowflakeConnection


def get_snowflake_config() -> dict:
    """
    Function to initialize and retrieve a valid Snowflake connection configuration to connect to it

    Returns:
        dict: A valid connection configuration
    """
    # Get credentials from environment secret
    sf_creds = json.loads(os.environ.get("SNOWFLAKE_CREDENTIALS"))

    # Initialize json config
    snowflake_config = {}
    snowflake_config["user"] = sf_creds["user"]
    snowflake_config["password"] = sf_creds["password"]
    snowflake_config["account"] = "missionlane.us-east-1"
    snowflake_config["warehouse"] = os.environ.get("SNOWFLAKE_WAREHOUSE")
    snowflake_config["database"] = os.environ.get("SNOWFLAKE_DATABASE")

    return snowflake_config

def connect_to_snowflake(logger: Logger) -> SnowflakeConnection:
    """
    Function to create a valid Snowflake connection based on the configuration received

    Args:
        logger (Logger): A Logger instance

    Raises:
        Exception: Connection to Snowflake failed

    Returns:
        SnowflakeConnection: A valid connection object (it must be closed at the end of the script)
    """
    # Get snowflake configuration
    snowflake_config = get_snowflake_config()

    # Try to connect to Snowflake
    try:
        # Create connection
        logger.info("Connecting to Snowflake")

        conn = snowflake.connector.connect(
            user=snowflake_config.get("user"),
            password=snowflake_config.get("password"),
            account=snowflake_config.get("account"),
            warehouse=snowflake_config.get("warehouse"),
            database=snowflake_config.get("database"),
            ocsp_fail_open=False,
            insecure_mode=True
        )
    except Exception as e:
        raise Exception(f"Connection to Snowflake failed: {e}")

    return conn

def run_query(query: str, logger: Logger) -> list:
    """
    Function to run a query in Snowflake

    Args:
        query (str): Query to run
        logger (Logger): A Logger instance

    Returns:
        list: Result set from Snowflake
    """
    # Connect to Snowflake
    conn = connect_to_snowflake(logger=logger)

    # Create cursor
    cursor = conn.cursor()

    # Run query
    try:
        logger.info(f"Running query {query}")
        cursor.execute(query)
    except Exception as e:
        conn.close()
        raise Exception(f"Failed to run query: {e}")

    # Close connection
    conn.close()

    return cursor.fetchall()
