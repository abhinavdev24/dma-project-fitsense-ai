"""
Chart Configuration and Helpers for FitSense AI Dashboard
Provides consistent Plotly chart styling based on design system.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict, Any, Tuple


# =============================================================================
# DESIGN TOKENS
# =============================================================================

# Color palette for charts
CHART_COLORS = [
    '#3B82F6',  # Blue
    '#F59E0B',  # Amber
    '#10B981',  # Green
    '#EF4444',  # Red
    '#8B5CF6',  # Purple
    '#EC4899',  # Pink
    '#06B6D4',  # Cyan
    '#F97316',  # Orange
]

# Chart templates
CHART_TEMPLATE = {
    'layout': {
        'paper_bgcolor': 'rgba(15, 23, 42, 0)',
        'plot_bgcolor': 'rgba(30, 41, 59, 0)',
        'font': {
            'family': 'Fira Sans, sans-serif',
            'color': '#F1F5F9',
            'size': 12
        },
        'colorway': CHART_COLORS,
        'xaxis': {
            'gridcolor': '#334155',
            'zerolinecolor': '#475569',
            'linecolor': '#475569',
            'tickfont': {'color': '#94A3B8'},
            'title_font': {'color': '#94A3B8'}
        },
        'yaxis': {
            'gridcolor': '#334155',
            'zerolinecolor': '#475569',
            'linecolor': '#475569',
            'tickfont': {'color': '#94A3B8'},
            'title_font': {'color': '#94A3B8'}
        },
        'legend': {
            'bgcolor': 'rgba(15, 23, 42, 0)',
            'font': {'color': '#94A3B8'},
            'bordercolor': '#334155',
            'borderwidth': 1
        },
        'hoverlabel': {
            'bgcolor': '#1E293B',
            'bordercolor': '#3B82F6',
            'font': {'color': '#F1F5F9', 'family': 'Fira Sans, sans-serif'}
        },
        'margin': {'t': 20, 'r': 20, 'b': 60, 'l': 60}
    }
}


def apply_dark_theme(fig: go.Figure) -> go.Figure:
    """
    Apply consistent dark theme styling to a Plotly figure.
    """
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 0)',
        plot_bgcolor='rgba(30, 41, 59, 0)',
        font=dict(
            family='Fira Sans, sans-serif',
            color='#F1F5F9',
            size=12
        ),
        hoverlabel=dict(
            bgcolor='#1E293B',
            bordercolor='#3B82F6',
            font=dict(color='#F1F5F9', family='Fira Sans, sans-serif')
        ),
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8'),
            bordercolor='#334155',
            borderwidth=1
        ),
        margin=dict(t=20, r=20, b=60, l=60)
    )
    return fig


def apply_axis_style(fig: go.Figure, xaxis: bool = True, yaxis: bool = True) -> go.Figure:
    """
    Apply consistent axis styling.
    """
    axis_style = {
        'gridcolor': '#334155',
        'zerolinecolor': '#475569',
        'linecolor': '#475569',
        'tickfont': {'color': '#94A3B8'},
        'title_font': {'color': '#94A3B8'}
    }
    
    if xaxis:
        fig.update_xaxes(**axis_style)
    if yaxis:
        fig.update_yaxes(**axis_style)
    
    return fig


# =============================================================================
# CHART FACTORY FUNCTIONS
# =============================================================================

def create_scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_axis_title: str = None,
    y_axis_title: str = None,
    color: str = None,
    size: str = None,
    hover_data: List[str] = None,
    trendline: str = None,
    color_discrete_sequence: List[str] = None
) -> go.Figure:
    """
    Create a scatter plot with dark theme styling.
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        hover_data=hover_data,
        trendline=trendline,
        color_discrete_sequence=color_discrete_sequence or CHART_COLORS,
        template='plotly_dark'
    )

    fig = apply_dark_theme(fig)
    fig = apply_axis_style(fig)

    # Update axis titles if provided
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title=dict(text=x_axis_title if x_axis_title else x, font=dict(color='#94A3B8'))),
        yaxis=dict(title=dict(text=y_axis_title if y_axis_title else y, font=dict(color='#94A3B8'))),
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8')
        )
    )
    
    # Update marker style
    fig.update_traces(
        marker=dict(
            size=8,
            line=dict(width=1, color='#1E293B')
        )
    )
    
    return fig


def create_histogram(
    df: pd.DataFrame,
    x: str,
    title: str,
    color: str = '#3B82F6',
    nbins: int = None
) -> go.Figure:
    """
    Create a histogram with dark theme styling.
    """
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        color_discrete_sequence=[color],
        template='plotly_dark'
    )
    
    fig = apply_dark_theme(fig)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        bargap=0.1
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='#1E293B')
        )
    )
    
    return fig


def create_pie_chart(
    df: pd.DataFrame,
    values: str,
    names: str,
    title: str,
    hole: float = 0.4,
    showLegend: bool = True
) -> go.Figure:
    """
    Create a pie/donut chart with dark theme styling.
    """
    fig = px.pie(
        df,
        values=values,
        names=names,
        hole=hole,
        color_discrete_sequence=CHART_COLORS,
        template='plotly_dark'
    )
    
    fig = apply_dark_theme(fig)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=showLegend,
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8'),
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        margin=dict(t=60, b=80, l=20, r=20)
    )
    
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        textfont=dict(color='#F1F5F9', family='Fira Sans, sans-serif')
    )
    
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    orientation: str = 'v',
    color: str = None,
    color_discrete_sequence: List[str] = None
) -> go.Figure:
    """
    Create a bar chart with dark theme styling.
    """
    fig = px.bar(
        df,
        x=x,
        y=y,
        orientation=orientation,
        color=color,
        color_discrete_sequence=color_discrete_sequence or CHART_COLORS,
        template='plotly_dark'
    )
    
    fig = apply_dark_theme(fig)
    fig = apply_axis_style(fig)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True if color else False,
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8')
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    # Update bar style
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='#1E293B')
        )
    )
    
    return fig


def create_box_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_axis_title: str = None,
    y_axis_title: str = None,
    color: str = None,
    color_discrete_sequence: List[str] = None
) -> go.Figure:
    """
    Create a box plot with dark theme styling.
    """
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=color_discrete_sequence or CHART_COLORS[:2],
        template='plotly_dark',
        points='outliers'
    )

    fig = apply_dark_theme(fig)
    fig = apply_axis_style(fig)

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title=dict(text=x_axis_title if x_axis_title else x, font=dict(color='#94A3B8'))),
        yaxis=dict(title=dict(text=y_axis_title if y_axis_title else y, font=dict(color='#94A3B8'))),
        showlegend=True if color else False,
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8')
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )

    # Update box style
    fig.update_traces(
        marker=dict(size=6),
        boxmean=True
    )

    return fig


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    x_axis_title: str = None,
    y_axis_title: str = None,
    color: str = None,
    fill: str = None,
    line_shape: str = 'linear',
    chart_type: str = 'line'
) -> go.Figure:
    """
    Create a line chart with dark theme styling.
    Optionally can render as a bar chart if chart_type='bar'.
    """
    if chart_type == 'bar':
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            color_discrete_sequence=CHART_COLORS,
            template='plotly_dark'
        )
    else:
        fig = px.line(
            df,
            x=x,
            y=y,
            color=color,
            color_discrete_sequence=CHART_COLORS,
            template='plotly_dark',
            line_shape=line_shape
        )

    fig = apply_dark_theme(fig)
    fig = apply_axis_style(fig)

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title=dict(text=x_axis_title if x_axis_title else x, font=dict(color='#94A3B8'))),
        yaxis=dict(title=dict(text=y_axis_title if y_axis_title else y, font=dict(color='#94A3B8'))),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8')
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )

    # Apply area fill if specified
    if fill:
        fig.update_traces(fill=fill, line=dict(width=2))

    return fig


def create_area_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    color: str = None,
    color_discrete_sequence: List[str] = None
) -> go.Figure:
    """
    Create an area chart with dark theme styling.
    """
    fig = px.area(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=color_discrete_sequence or CHART_COLORS,
        template='plotly_dark'
    )
    
    fig = apply_dark_theme(fig)
    fig = apply_axis_style(fig)
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='#F1F5F9'),
            x=0.5,
            xanchor='center'
        ),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0)',
            font=dict(color='#94A3B8')
        ),
        margin=dict(t=60, b=60, l=60, r=60)
    )
    
    return fig


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_empty_state_message(message: str, chart_type: str = "chart") -> go.Figure:
    """
    Create an empty state figure for when no data is available.
    """
    fig = go.Figure()
    
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            size=14,
            color='#94A3B8',
            family='Fira Sans, sans-serif'
        )
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(30, 41, 59, 0.5)',
        plot_bgcolor='rgba(30, 41, 59, 0.5)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=300,
        margin=dict(t=20, r=20, b=20, l=20)
    )
    
    return fig


def format_number(num: float) -> str:
    """
    Format a number with appropriate suffixes (K, M, B).
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)


def create_dataframe_table(
    df: pd.DataFrame,
    title: str = None,
    max_rows: int = None
) -> go.Figure:
    """
    Create a styled table visualization from a pandas DataFrame.
    """
    # Limit rows if specified
    display_df = df.head(max_rows) if max_rows else df

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(display_df.columns),
            fill_color='#1E293B',
            align='left',
            font=dict(color='#F1F5F9', size=12, family='Fira Sans, sans-serif'),
            height=36
        ),
        cells=dict(
            values=[display_df[col] for col in display_df.columns],
            fill_color='#0F172A',
            align='left',
            font=dict(color='#E2E8F0', size=11, family='Fira Sans, sans-serif'),
            height=32
        )
    )])

    fig = apply_dark_theme(fig)

    if title:
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color='#F1F5F9'),
                x=0.5,
                xanchor='center'
            ),
            margin=dict(t=60, b=30, l=20, r=20)
        )
    else:
        fig.update_layout(
            margin=dict(t=20, r=20, b=20, l=20)
        )

    return fig


def create_kpi_card(
    label: str,
    value: Any,
    delta: Any = None,
    help_text: str = None
) -> None:
    """
    Create a styled KPI metric card.
    """
    import streamlit as st

    col1, col2 = st.columns([1, 3])

    with col1:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            help=help_text
        )


# =============================================================================
# CHART CONFIGURATION PRESETS
# =============================================================================

def get_chart_config() -> Dict[str, Any]:
    """
    Get global chart configuration for Plotly.
    """
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'select2d',
            'lasso2d',
            'autoScale2d',
            'resetScale2d',
            'hoverClosestCartesian',
            'hoverCompareCartesian',
            'toggleSpikelines'
        ],
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'fitsense_chart',
            'height': 600,
            'width': 800,
            'scale': 2
        }
    }


# Export all chart functions
__all__ = [
    'apply_dark_theme',
    'apply_axis_style',
    'create_scatter_chart',
    'create_scatter_plot',  # Alias
    'create_histogram',
    'create_pie_chart',
    'create_bar_chart',
    'create_box_plot',
    'create_line_chart',
    'create_area_chart',
    'create_dataframe_table',
    'create_empty_state_message',
    'format_number',
    'create_kpi_card',
    'get_chart_config',
    'CHART_COLORS',
    'COLOR_PALETTE',  # Alias
    'fitsense_template',  # Alias
    'CHART_TEMPLATE',
]

# Aliases for backward compatibility
fitsense_template = CHART_TEMPLATE
COLOR_PALETTE = CHART_COLORS
create_scatter_plot = create_scatter_chart
