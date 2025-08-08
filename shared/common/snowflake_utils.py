"""
Snowflake connection and query utilities.

This module provides common functions for connecting to Snowflake
and executing queries across different Streamlit applications.
"""

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import Session
from typing import Optional, Dict, Any, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_snowflake_connection() -> Session:
    """
    Get an active Snowflake session.
    
    This function tries to get the active session from Snowpark.
    If running in Snowflake (SiS), it uses the active session.
    For local development, you would need to configure connection parameters.
    
    Returns:
        Session: Active Snowflake session
        
    Raises:
        Exception: If unable to establish connection
    """
    try:
        # Try to get active session (works in Snowflake SiS environment)
        session = get_active_session()
        logger.info("Using active Snowflake session")
        return session
    except Exception as e:
        logger.error(f"Failed to get active session: {e}")
        # For local development, you might want to create a session here
        # This would require connection parameters
        raise Exception("Unable to establish Snowflake connection. Ensure you're running in Snowflake or configure local connection.")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Parameters for parameterized queries
        
    Returns:
        pd.DataFrame: Query results
        
    Raises:
        Exception: If query execution fails
    """
    try:
        session = get_snowflake_connection()
        
        if params:
            # For parameterized queries, you might need to format them
            # This is a simple example - consider using proper parameterization
            query = query.format(**params)
            
        logger.info(f"Executing query: {query[:100]}...")
        result = session.sql(query).to_pandas()
        logger.info(f"Query returned {len(result)} rows")
        
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        st.error(f"Database query failed: {str(e)}")
        return pd.DataFrame()


def get_warehouse_info() -> Dict[str, Any]:
    """
    Get information about the current warehouse.
    
    Returns:
        dict: Warehouse information
    """
    try:
        query = "SELECT CURRENT_WAREHOUSE() as warehouse, CURRENT_DATABASE() as database, CURRENT_SCHEMA() as schema"
        result = execute_query(query)
        
        if not result.empty:
            return {
                'warehouse': result.iloc[0]['WAREHOUSE'],
                'database': result.iloc[0]['DATABASE'], 
                'schema': result.iloc[0]['SCHEMA']
            }
    except Exception as e:
        logger.error(f"Failed to get warehouse info: {e}")
        
    return {'warehouse': 'Unknown', 'database': 'Unknown', 'schema': 'Unknown'}


def test_connection() -> bool:
    """
    Test the Snowflake connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        execute_query("SELECT 1 as test")
        return True
    except Exception:
        return False


def get_table_info(table_name: str, schema_name: Optional[str] = None) -> pd.DataFrame:
    """
    Get information about a table's columns.
    
    Args:
        table_name (str): Name of the table
        schema_name (str, optional): Schema name (uses current if not specified)
        
    Returns:
        pd.DataFrame: Table column information
    """
    try:
        if schema_name:
            query = f"DESCRIBE TABLE {schema_name}.{table_name}"
        else:
            query = f"DESCRIBE TABLE {table_name}"
            
        return execute_query(query)
        
    except Exception as e:
        logger.error(f"Failed to get table info for {table_name}: {e}")
        return pd.DataFrame()


def execute_dml(query: str, params: Optional[Dict[str, Any]] = None) -> bool:
    """
    Execute a DML statement (INSERT, UPDATE, DELETE).
    
    Args:
        query (str): DML query to execute
        params (dict, optional): Parameters for parameterized queries
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        session = get_snowflake_connection()
        
        if params:
            query = query.format(**params)
            
        logger.info(f"Executing DML: {query[:100]}...")
        session.sql(query).collect()
        logger.info("DML executed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"DML execution failed: {e}")
        st.error(f"Database operation failed: {str(e)}")
        return False 