"""
Data processing and utility functions for Streamlit applications.

This module provides common data manipulation, formatting, and generation
functions that can be used across different Streamlit applications.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_sample_data(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Load sample data - this would normally execute a query against Snowflake.
    For demo purposes, returns sample data.
    
    Args:
        query (str): SQL query to execute (ignored in demo)
        params (dict, optional): Parameters for parameterized queries (ignored in demo)
        
    Returns:
        pd.DataFrame: Sample data
    """
    # In a real implementation, this would use snowflake_utils.execute_query
    # For demo purposes, return sample data
    logger.info("Loading sample data (demo mode)")
    
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'revenue': np.random.normal(10000, 2000, 30),
        'orders': np.random.poisson(50, 30),
        'customers': np.random.poisson(30, 30)
    })


def process_data(df: pd.DataFrame, operations: List[str]) -> pd.DataFrame:
    """
    Process DataFrame with specified operations.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        operations (list): List of operations to apply
        
    Returns:
        pd.DataFrame: Processed DataFrame
    """
    try:
        processed_df = df.copy()
        
        for operation in operations:
            if operation == 'remove_nulls':
                processed_df = processed_df.dropna()
            elif operation == 'remove_duplicates':
                processed_df = processed_df.drop_duplicates()
            elif operation == 'sort_by_date':
                if 'date' in processed_df.columns:
                    processed_df = processed_df.sort_values('date')
            elif operation == 'add_month_column':
                if 'date' in processed_df.columns:
                    processed_df['month'] = pd.to_datetime(processed_df['date']).dt.month
                    
        logger.info(f"Data processed with operations: {operations}")
        return processed_df
        
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        return df


def format_currency(value: Union[int, float], currency: str = "USD") -> str:
    """
    Format numeric value as currency.
    
    Args:
        value: Numeric value to format
        currency: Currency code (default: USD)
        
    Returns:
        str: Formatted currency string
    """
    try:
        if currency == "USD":
            return f"${value:,.2f}"
        elif currency == "EUR":
            return f"€{value:,.2f}"
        elif currency == "GBP":
            return f"£{value:,.2f}"
        else:
            return f"{value:,.2f} {currency}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format numeric value as percentage.
    
    Args:
        value: Numeric value to format (as decimal, e.g., 0.15 for 15%)
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    try:
        return f"{value * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return str(value)


def validate_data_frame(df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
    """
    Validate DataFrame structure and content.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        dict: Validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'null_count': df.isnull().sum().sum()
        }
    }
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation_results['is_valid'] = False
        validation_results['errors'].append(f"Missing required columns: {missing_columns}")
    
    # Check for empty DataFrame
    if len(df) == 0:
        validation_results['warnings'].append("DataFrame is empty")
    
    # Check for high null percentage
    null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if null_percentage > 20:
        validation_results['warnings'].append(f"High null percentage: {null_percentage:.1f}%")
    
    return validation_results


@st.cache_data
def generate_sample_data(days: int = 30) -> pd.DataFrame:
    """
    Generate sample time series data for demo purposes.
    
    Args:
        days: Number of days of data to generate
        
    Returns:
        pd.DataFrame: Sample time series data
    """
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # Generate correlated sample data
    base_revenue = 8000
    trend = np.linspace(0, 2000, days)  # Upward trend
    seasonality = 1000 * np.sin(2 * np.pi * np.arange(days) / 7)  # Weekly pattern
    noise = np.random.normal(0, 500, days)
    
    revenue = base_revenue + trend + seasonality + noise
    revenue = np.maximum(revenue, 1000)  # Ensure positive values
    
    return pd.DataFrame({
        'date': dates,
        'revenue': revenue.round(2),
        'orders': np.random.poisson(revenue / 150),  # Orders correlated with revenue
        'customers': np.random.poisson(revenue / 200),  # Customers correlated with revenue
        'avg_order_value': (revenue / np.maximum(1, revenue / 150)).round(2)
    })


@st.cache_data
def generate_customer_data(customers: int = 100) -> pd.DataFrame:
    """
    Generate sample customer data for analytics.
    
    Args:
        customers: Number of customers to generate
        
    Returns:
        pd.DataFrame: Sample customer data
    """
    np.random.seed(42)  # For reproducible results
    
    # Generate customer segments
    segments = np.random.choice(['Premium', 'Standard', 'Basic'], customers, p=[0.1, 0.4, 0.5])
    
    # Generate data based on segments
    data = []
    for i in range(customers):
        segment = segments[i]
        
        if segment == 'Premium':
            orders = np.random.poisson(15)
            avg_order = np.random.normal(300, 50)
        elif segment == 'Standard':
            orders = np.random.poisson(8)
            avg_order = np.random.normal(150, 30)
        else:  # Basic
            orders = np.random.poisson(4)
            avg_order = np.random.normal(75, 20)
        
        total_spent = orders * max(avg_order, 10)  # Ensure positive values
        
        data.append({
            'customer_id': f'CUST_{i+1:04d}',
            'segment': segment,
            'total_orders': max(orders, 1),
            'total_spent': round(total_spent, 2),
            'avg_order_value': round(total_spent / max(orders, 1), 2),
            'tenure_months': np.random.randint(1, 36),
            'last_order_days': np.random.randint(1, 90)
        })
    
    return pd.DataFrame(data)


@st.cache_data
def generate_trend_data(days: int = 90) -> pd.DataFrame:
    """
    Generate sample trend data for forecasting demos.
    
    Args:
        days: Number of days of data to generate
        
    Returns:
        pd.DataFrame: Sample trend data
    """
    dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # Generate trend with growth
    base_value = 1000
    growth_rate = 0.02  # 2% growth over the period
    trend = base_value * (1 + growth_rate * np.arange(days) / days)
    
    # Add seasonality and noise
    seasonality = 200 * np.sin(2 * np.pi * np.arange(days) / 30)  # Monthly pattern
    noise = np.random.normal(0, 50, days)
    
    daily_sales = trend + seasonality + noise
    daily_sales = np.maximum(daily_sales, 100)  # Ensure positive values
    
    cumulative_sales = np.cumsum(daily_sales)
    
    return pd.DataFrame({
        'date': dates,
        'daily_sales': daily_sales.round(2),
        'cumulative_sales': cumulative_sales.round(2),
        'moving_avg_7d': pd.Series(daily_sales).rolling(window=7, min_periods=1).mean().round(2),
        'moving_avg_30d': pd.Series(daily_sales).rolling(window=30, min_periods=1).mean().round(2)
    })


def calculate_growth_rate(current_value: float, previous_value: float) -> float:
    """
    Calculate percentage growth rate between two values.
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
        
    Returns:
        float: Growth rate as decimal (e.g., 0.15 for 15% growth)
    """
    try:
        if previous_value == 0:
            return 0.0
        return (current_value - previous_value) / previous_value
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def create_pivot_table(df: pd.DataFrame, 
                      index_col: str, 
                      value_col: str, 
                      agg_func: str = 'sum') -> pd.DataFrame:
    """
    Create a pivot table from DataFrame.
    
    Args:
        df: Input DataFrame
        index_col: Column to use as index
        value_col: Column to aggregate
        agg_func: Aggregation function ('sum', 'mean', 'count', etc.)
        
    Returns:
        pd.DataFrame: Pivot table
    """
    try:
        pivot = df.pivot_table(
            index=index_col,
            values=value_col,
            aggfunc=agg_func,
            fill_value=0
        )
        return pivot.reset_index()
    except Exception as e:
        logger.error(f"Pivot table creation failed: {e}")
        return pd.DataFrame()


def filter_data_by_date_range(df: pd.DataFrame, 
                             date_col: str, 
                             start_date: str, 
                             end_date: str) -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: Input DataFrame
        date_col: Name of date column
        start_date: Start date (string format)
        end_date: End date (string format)
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        mask = (df_copy[date_col] >= start_date) & (df_copy[date_col] <= end_date)
        return df_copy[mask]
        
    except Exception as e:
        logger.error(f"Date filtering failed: {e}")
        return df 