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


def display_metric(title: str, value: str, delta: Optional[str] = None) -> None:
    """
    Display a single metric with optional delta.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta value
    """
    st.metric(title, value, delta)


def display_metrics(metrics: Dict[str, Union[float, int]], 
                   columns: int = 4,
                   format_func: Optional[Dict[str, str]] = None) -> None:
    """
    Display metrics in a row of columns.
    
    Args:
        metrics: Dictionary of metric name to value
        columns: Number of columns to display
        format_func: Optional formatting functions for each metric
    """
    cols = st.columns(columns)
    
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i % columns]:
            # Apply formatting if provided
            if format_func and key in format_func:
                if format_func[key] == 'currency':
                    formatted_value = f"${value:,.2f}"
                elif format_func[key] == 'percentage':
                    formatted_value = f"{value:.1%}"
                elif format_func[key] == 'number':
                    formatted_value = f"{value:,.0f}"
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)
            
            st.metric(key.replace('_', ' ').title(), formatted_value)


def display_dataframe(df: pd.DataFrame, 
                     height: Optional[int] = None,
                     use_container_width: bool = True) -> None:
    """
    Display a DataFrame with optional styling.
    
    Args:
        df: DataFrame to display
        height: Optional height in pixels
        use_container_width: Whether to use container width
    """
    st.dataframe(df, height=height, use_container_width=use_container_width)


def create_data_table(df: pd.DataFrame,
                     title: Optional[str] = None,
                     show_index: bool = False,
                     max_rows: Optional[int] = None) -> None:
    """
    Create a formatted data table with optional title.
    
    Args:
        df: DataFrame to display
        title: Optional table title
        show_index: Whether to show the index
        max_rows: Maximum number of rows to display
    """
    if title:
        st.subheader(title)
    
    display_df = df.copy()
    if max_rows and len(display_df) > max_rows:
        display_df = display_df.head(max_rows)
        st.caption(f"Showing first {max_rows} of {len(df)} rows")
    
    st.dataframe(display_df, use_container_width=True, hide_index=not show_index)


def create_line_chart(df: pd.DataFrame,
                     x_col: str,
                     y_col: str,
                     title: Optional[str] = None,
                     color_col: Optional[str] = None) -> None:
    """
    Create a line chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Optional chart title
        color_col: Optional column for color grouping
    """
    try:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=bool(color_col)
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating line chart: {e}")
        st.error(f"Failed to create line chart: {str(e)}")


def create_bar_chart(df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    title: Optional[str] = None,
                    color_col: Optional[str] = None,
                    orientation: str = 'v') -> None:
    """
    Create a bar chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Optional chart title
        color_col: Optional column for color grouping
        orientation: Chart orientation ('v' for vertical, 'h' for horizontal)
    """
    try:
        if orientation == 'h':
            fig = px.bar(df, x=y_col, y=x_col, color=color_col, title=title, orientation='h')
        else:
            fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=bool(color_col)
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        st.error(f"Failed to create bar chart: {str(e)}")


def create_pie_chart(df: pd.DataFrame,
                    names_col: str,
                    values_col: str,
                    title: Optional[str] = None) -> None:
    """
    Create a pie chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        names_col: Column name for pie slice labels
        values_col: Column name for pie slice values
        title: Optional chart title
    """
    try:
        fig = px.pie(df, names=names_col, values=values_col, title=title)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        st.error(f"Failed to create pie chart: {str(e)}")


def create_scatter_plot(df: pd.DataFrame,
                       x_col: str,
                       y_col: str,
                       title: Optional[str] = None,
                       color_col: Optional[str] = None,
                       size_col: Optional[str] = None) -> None:
    """
    Create a scatter plot using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Optional chart title
        color_col: Optional column for color grouping
        size_col: Optional column for point sizes
    """
    try:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=bool(color_col)
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        st.error(f"Failed to create scatter plot: {str(e)}")


def create_area_chart(df: pd.DataFrame,
                     x_col: str,
                     y_col: str,
                     title: Optional[str] = None,
                     color_col: Optional[str] = None) -> None:
    """
    Create an area chart using Plotly.
    
    Args:
        df: DataFrame containing the data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Optional chart title
        color_col: Optional column for color grouping
    """
    try:
        fig = px.area(df, x=x_col, y=y_col, color=color_col, title=title)
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            showlegend=bool(color_col)
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Error creating area chart: {e}")
        st.error(f"Failed to create area chart: {str(e)}")


def create_filter_sidebar(df: pd.DataFrame,
                         filter_columns: List[str],
                         sidebar_title: str = "Filters") -> Dict[str, Any]:
    """
    Create filter controls in the sidebar.
    
    Args:
        df: DataFrame to create filters for
        filter_columns: List of column names to create filters for
        sidebar_title: Title for the filter section
        
    Returns:
        dict: Dictionary of filter values
    """
    filters = {}
    
    with st.sidebar:
        st.subheader(sidebar_title)
        
        for col in filter_columns:
            if col in df.columns:
                unique_values = df[col].unique()
                
                if df[col].dtype in ['object', 'string']:
                    # Create multiselect for categorical data
                    selected = st.multiselect(
                        f"Select {col.replace('_', ' ').title()}:",
                        options=unique_values,
                        default=unique_values
                    )
                    filters[col] = selected
                    
                elif df[col].dtype in ['int64', 'float64']:
                    # Create slider for numeric data
                    min_val = float(df[col].min())
                    max_val = float(df[col].max())
                    selected_range = st.slider(
                        f"{col.replace('_', ' ').title()} Range:",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val)
                    )
                    filters[col] = selected_range
    
    return filters


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to a DataFrame.
    
    Args:
        df: DataFrame to filter
        filters: Dictionary of filter values
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for col, filter_value in filters.items():
        if col in filtered_df.columns:
            if isinstance(filter_value, list) and filter_value:
                # Handle multiselect filters
                filtered_df = filtered_df[filtered_df[col].isin(filter_value)]
            elif isinstance(filter_value, tuple) and len(filter_value) == 2:
                # Handle range filters
                min_val, max_val = filter_value
                filtered_df = filtered_df[
                    (filtered_df[col] >= min_val) & 
                    (filtered_df[col] <= max_val)
                ]
    
    return filtered_df


def create_download_button(df: pd.DataFrame,
                          filename: str,
                          button_text: str = "Download CSV",
                          mime_type: str = "text/csv") -> None:
    """
    Create a download button for DataFrame data.
    
    Args:
        df: DataFrame to download
        filename: Filename for the download
        button_text: Text to display on the button
        mime_type: MIME type for the download
    """
    try:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label=button_text,
            data=csv_data,
            file_name=filename,
            mime=mime_type
        )
    except Exception as e:
        logger.error(f"Error creating download button: {e}")
        st.error(f"Failed to create download button: {str(e)}")


def show_data_info(df: pd.DataFrame) -> None:
    """
    Show information about a DataFrame.
    
    Args:
        df: DataFrame to analyze
    """
    with st.expander("📊 Data Information"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Show column info
        st.subheader("Column Information")
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.astype(str),
            'Null Count': df.isnull().sum(),
            'Null %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        st.dataframe(info_df, use_container_width=True)


def create_alert(message: str, alert_type: str = "info") -> None:
    """
    Create a styled alert message.
    
    Args:
        message: Alert message
        alert_type: Type of alert ('info', 'success', 'warning', 'error')
    """
    if alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.info(message) 