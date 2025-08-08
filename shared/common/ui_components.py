"""
Reusable UI components for Streamlit applications.

This module provides common UI elements and layouts that can be
shared across different Streamlit applications.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


def create_sidebar(title: str = "Navigation", options: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Create a standardized sidebar with navigation options.
    
    Args:
        title (str): Sidebar title
        options (list): List of navigation options
        
    Returns:
        str: Selected option
    """
    with st.sidebar:
        st.title(title)
        
        if options:
            option_labels = [opt['label'] for opt in options]
            selected = st.selectbox("Choose an option:", option_labels)
            
            # Find the selected option
            for opt in options:
                if opt['label'] == selected:
                    return opt.get('value', selected)
        
        return ""


def display_metrics(metrics: Dict[str, Union[float, int]], 
                   columns: int = 4,
                   format_func: Optional[Dict[str, str]] = None) -> None:
    """
    Display metrics in a row of columns.
    
    Args:
        metrics (dict): Dictionary of metric names and values
        columns (int): Number of columns to display
        format_func (dict): Dictionary of format functions for each metric
    """
    if not metrics:
        return
        
    metric_items = list(metrics.items())
    cols = st.columns(columns)
    
    for i, (name, value) in enumerate(metric_items):
        col_index = i % columns
        with cols[col_index]:
            if format_func and name in format_func:
                formatted_value = format_func[name].format(value)
            else:
                if isinstance(value, float):
                    formatted_value = f"{value:,.2f}"
                elif isinstance(value, int):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = str(value)
                    
            st.metric(
                label=name.replace('_', ' ').title(),
                value=formatted_value
            )


def create_data_table(df: pd.DataFrame, 
                     title: str = "Data Table",
                     height: int = 400,
                     use_container_width: bool = True) -> None:
    """
    Create a formatted data table with optional title.
    
    Args:
        df (pd.DataFrame): DataFrame to display
        title (str): Table title
        height (int): Table height in pixels
        use_container_width (bool): Whether to use container width
    """
    if title:
        st.subheader(title)
        
    if df.empty:
        st.info("No data available")
        return
        
    st.dataframe(
        df,
        height=height,
        use_container_width=use_container_width
    )


def create_line_chart(df: pd.DataFrame,
                     x_column: str,
                     y_column: str,
                     title: str = "Line Chart",
                     color_column: Optional[str] = None) -> None:
    """
    Create a line chart using Plotly.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_column (str): Column name for x-axis
        y_column (str): Column name for y-axis
        title (str): Chart title
        color_column (str, optional): Column name for color grouping
    """
    if df.empty:
        st.info("No data available for chart")
        return
        
    try:
        fig = px.line(
            df,
            x=x_column,
            y=y_column,
            color=color_column,
            title=title
        )
        
        fig.update_layout(
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title(),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        st.error(f"Failed to create chart: {str(e)}")


def create_bar_chart(df: pd.DataFrame,
                    x_column: str,
                    y_column: str,
                    title: str = "Bar Chart",
                    orientation: str = 'v') -> None:
    """
    Create a bar chart using Plotly.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        x_column (str): Column name for x-axis
        y_column (str): Column name for y-axis
        title (str): Chart title
        orientation (str): Chart orientation ('v' for vertical, 'h' for horizontal)
    """
    if df.empty:
        st.info("No data available for chart")
        return
        
    try:
        fig = px.bar(
            df,
            x=x_column if orientation == 'v' else y_column,
            y=y_column if orientation == 'v' else x_column,
            title=title,
            orientation=orientation
        )
        
        fig.update_layout(
            xaxis_title=x_column.replace('_', ' ').title(),
            yaxis_title=y_column.replace('_', ' ').title()
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        st.error(f"Failed to create chart: {str(e)}")


def create_pie_chart(df: pd.DataFrame,
                    labels_column: str,
                    values_column: str,
                    title: str = "Pie Chart") -> None:
    """
    Create a pie chart using Plotly.
    
    Args:
        df (pd.DataFrame): DataFrame with data
        labels_column (str): Column name for labels
        values_column (str): Column name for values
        title (str): Chart title
    """
    if df.empty:
        st.info("No data available for chart")
        return
        
    try:
        fig = px.pie(
            df,
            names=labels_column,
            values=values_column,
            title=title
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        st.error(f"Failed to create chart: {str(e)}")


def create_filter_sidebar(df: pd.DataFrame, 
                         filter_columns: List[str],
                         title: str = "Filters") -> Dict[str, Any]:
    """
    Create filters in the sidebar for DataFrame columns.
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        filter_columns (list): List of column names to create filters for
        title (str): Filter section title
        
    Returns:
        dict: Dictionary of selected filter values
    """
    filters = {}
    
    with st.sidebar:
        st.subheader(title)
        
        for column in filter_columns:
            if column in df.columns:
                if df[column].dtype in ['object', 'string']:
                    # Categorical filter
                    unique_values = sorted(df[column].dropna().unique().tolist())
                    selected = st.multiselect(
                        f"Select {column.replace('_', ' ').title()}:",
                        options=unique_values,
                        default=unique_values
                    )
                    filters[column] = selected
                    
                elif pd.api.types.is_numeric_dtype(df[column]):
                    # Numeric range filter
                    min_val = float(df[column].min())
                    max_val = float(df[column].max())
                    selected_range = st.slider(
                        f"{column.replace('_', ' ').title()} Range:",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val)
                    )
                    filters[column] = selected_range
                    
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    # Date range filter
                    min_date = df[column].min().date()
                    max_date = df[column].max().date()
                    selected_dates = st.date_input(
                        f"{column.replace('_', ' ').title()} Range:",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    filters[column] = selected_dates
    
    return filters


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        filters (dict): Dictionary of filter values
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    result_df = df.copy()
    
    for column, filter_value in filters.items():
        if column in result_df.columns and filter_value:
            try:
                if isinstance(filter_value, list) and len(filter_value) > 0:
                    # Categorical filter
                    result_df = result_df[result_df[column].isin(filter_value)]
                    
                elif isinstance(filter_value, tuple) and len(filter_value) == 2:
                    # Range filter
                    min_val, max_val = filter_value
                    result_df = result_df[
                        (result_df[column] >= min_val) & 
                        (result_df[column] <= max_val)
                    ]
                    
            except Exception as e:
                logger.error(f"Error applying filter for {column}: {e}")
                st.warning(f"Failed to apply filter for {column}")
    
    return result_df


def create_download_button(df: pd.DataFrame, 
                          filename: str = "data.csv",
                          button_text: str = "Download CSV") -> None:
    """
    Create a download button for DataFrame data.
    
    Args:
        df (pd.DataFrame): DataFrame to download
        filename (str): Filename for download
        button_text (str): Button text
    """
    if df.empty:
        return
        
    try:
        csv = df.to_csv(index=False)
        st.download_button(
            label=button_text,
            data=csv,
            file_name=filename,
            mime='text/csv'
        )
    except Exception as e:
        logger.error(f"Error creating download button: {e}")
        st.error("Failed to create download button")


def show_data_info(df: pd.DataFrame) -> None:
    """
    Display information about the DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to analyze
    """
    if df.empty:
        st.info("No data to display")
        return
        
    with st.expander("Data Information"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
        st.subheader("Column Information")
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Unique Values': df.nunique()
        })
        st.dataframe(info_df, use_container_width=True)


def create_alert(message: str, alert_type: str = "info") -> None:
    """
    Create a styled alert message.
    
    Args:
        message (str): Alert message
        alert_type (str): Type of alert ('info', 'success', 'warning', 'error')
    """
    if alert_type == "info":
        st.info(message)
    elif alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.write(message) 