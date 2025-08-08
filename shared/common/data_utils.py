"""
Data processing utilities for Streamlit applications.

This module provides common functions for data loading, processing,
and transformation that can be shared across applications.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, List, Dict, Any, Union
import logging
from .snowflake_utils import execute_query

logger = logging.getLogger(__name__)


@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data(query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Load data using a SQL query with caching.
    
    Args:
        query (str): SQL query to execute
        params (dict, optional): Parameters for the query
        
    Returns:
        pd.DataFrame: Loaded data
    """
    return execute_query(query, params)


def process_data(df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply a series of operations to a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        operations (list): List of operations to apply
        
    Returns:
        pd.DataFrame: Processed DataFrame
    """
    result_df = df.copy()
    
    for operation in operations:
        op_type = operation.get('type')
        
        try:
            if op_type == 'filter':
                condition = operation.get('condition')
                if condition:
                    result_df = result_df.query(condition)
                    
            elif op_type == 'sort':
                columns = operation.get('columns', [])
                ascending = operation.get('ascending', True)
                if columns:
                    result_df = result_df.sort_values(columns, ascending=ascending)
                    
            elif op_type == 'group':
                group_cols = operation.get('group_by', [])
                agg_ops = operation.get('aggregations', {})
                if group_cols and agg_ops:
                    result_df = result_df.groupby(group_cols).agg(agg_ops).reset_index()
                    
            elif op_type == 'rename':
                columns = operation.get('columns', {})
                if columns:
                    result_df = result_df.rename(columns=columns)
                    
            elif op_type == 'drop':
                columns = operation.get('columns', [])
                if columns:
                    result_df = result_df.drop(columns=columns, errors='ignore')
                    
            elif op_type == 'fillna':
                value = operation.get('value', 0)
                result_df = result_df.fillna(value)
                
        except Exception as e:
            logger.error(f"Error applying operation {op_type}: {e}")
            st.warning(f"Failed to apply operation: {op_type}")
    
    return result_df


def format_numbers(df: pd.DataFrame, number_columns: List[str], format_type: str = 'currency') -> pd.DataFrame:
    """
    Format numeric columns in a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        number_columns (list): List of columns to format
        format_type (str): Type of formatting ('currency', 'percentage', 'thousands')
        
    Returns:
        pd.DataFrame: DataFrame with formatted columns
    """
    result_df = df.copy()
    
    for col in number_columns:
        if col in result_df.columns:
            try:
                if format_type == 'currency':
                    result_df[col] = result_df[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "")
                elif format_type == 'percentage':
                    result_df[col] = result_df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "")
                elif format_type == 'thousands':
                    result_df[col] = result_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "")
            except Exception as e:
                logger.error(f"Error formatting column {col}: {e}")
    
    return result_df


def calculate_metrics(df: pd.DataFrame, metric_configs: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate various metrics from a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        metric_configs (list): List of metric configurations
        
    Returns:
        dict: Calculated metrics
    """
    metrics = {}
    
    for config in metric_configs:
        metric_name = config.get('name')
        metric_type = config.get('type')
        column = config.get('column')
        
        try:
            if metric_type == 'sum' and column in df.columns:
                metrics[metric_name] = df[column].sum()
            elif metric_type == 'mean' and column in df.columns:
                metrics[metric_name] = df[column].mean()
            elif metric_type == 'count':
                metrics[metric_name] = len(df)
            elif metric_type == 'max' and column in df.columns:
                metrics[metric_name] = df[column].max()
            elif metric_type == 'min' and column in df.columns:
                metrics[metric_name] = df[column].min()
                
        except Exception as e:
            logger.error(f"Error calculating metric {metric_name}: {e}")
            metrics[metric_name] = 0
    
    return metrics


def pivot_data(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc: str = 'sum') -> pd.DataFrame:
    """
    Create a pivot table from the DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        index (str): Column to use as index
        columns (str): Column to use as columns
        values (str): Column to use as values
        aggfunc (str): Aggregation function
        
    Returns:
        pd.DataFrame: Pivot table
    """
    try:
        return df.pivot_table(
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        ).reset_index()
    except Exception as e:
        logger.error(f"Error creating pivot table: {e}")
        return pd.DataFrame()


def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    Detect outliers in a numeric column.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        column (str): Column to analyze
        method (str): Method to use ('iqr' or 'zscore')
        
    Returns:
        pd.DataFrame: DataFrame with outlier flag
    """
    result_df = df.copy()
    
    try:
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            result_df['is_outlier'] = (df[column] < lower_bound) | (df[column] > upper_bound)
            
        elif method == 'zscore':
            from scipy import stats
            z_scores = np.abs(stats.zscore(df[column].dropna()))
            result_df['is_outlier'] = False
            result_df.loc[df[column].dropna().index, 'is_outlier'] = z_scores > 3
            
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        result_df['is_outlier'] = False
    
    return result_df


def create_time_series(df: pd.DataFrame, date_column: str, value_column: str, 
                      frequency: str = 'D') -> pd.DataFrame:
    """
    Create a time series from the DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        date_column (str): Date column name
        value_column (str): Value column name
        frequency (str): Frequency for resampling ('D', 'W', 'M', 'Q', 'Y')
        
    Returns:
        pd.DataFrame: Time series DataFrame
    """
    try:
        result_df = df.copy()
        result_df[date_column] = pd.to_datetime(result_df[date_column])
        result_df = result_df.set_index(date_column)
        
        # Resample based on frequency
        if frequency in ['D', 'W', 'M', 'Q', 'Y']:
            result_df = result_df[value_column].resample(frequency).sum().reset_index()
        else:
            result_df = result_df.reset_index()
            
        return result_df
        
    except Exception as e:
        logger.error(f"Error creating time series: {e}")
        return pd.DataFrame()


def validate_data(df: pd.DataFrame, validation_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate DataFrame against a set of rules.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        validation_rules (list): List of validation rules
        
    Returns:
        dict: Validation results
    """
    results = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    for rule in validation_rules:
        rule_type = rule.get('type')
        column = rule.get('column')
        
        try:
            if rule_type == 'not_null' and column in df.columns:
                null_count = df[column].isnull().sum()
                if null_count > 0:
                    results['errors'].append(f"Column {column} has {null_count} null values")
                    results['is_valid'] = False
                    
            elif rule_type == 'unique' and column in df.columns:
                duplicate_count = df[column].duplicated().sum()
                if duplicate_count > 0:
                    results['errors'].append(f"Column {column} has {duplicate_count} duplicates")
                    results['is_valid'] = False
                    
            elif rule_type == 'range' and column in df.columns:
                min_val = rule.get('min')
                max_val = rule.get('max')
                if min_val is not None:
                    below_min = (df[column] < min_val).sum()
                    if below_min > 0:
                        results['warnings'].append(f"Column {column} has {below_min} values below {min_val}")
                if max_val is not None:
                    above_max = (df[column] > max_val).sum()
                    if above_max > 0:
                        results['warnings'].append(f"Column {column} has {above_max} values above {max_val}")
                        
        except Exception as e:
            logger.error(f"Error in validation rule {rule_type}: {e}")
            results['errors'].append(f"Validation error: {str(e)}")
            results['is_valid'] = False
    
    return results 