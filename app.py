"""
GO Transit Dashboard - Home Page
Professional transit monitoring and analytics platform
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from route_data import get_route_name

# Page config
st.set_page_config(
    page_title="GO Transit Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Grafana-Style Dark Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        padding: 2rem 2rem;
        background-color: #181b1f;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* Override Streamlit default backgrounds */
    .stApp {
        background-color: #181b1f;
    }

    /* Metric cards - dark theme */
    .stMetric {
        background: transparent;
        padding: 0;
        border: none;
        box-shadow: none;
    }
    .stMetric label {
        color: #9fa3a8 !important;
        font-weight: 500;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #d8d9da !important;
        font-size: 1.875rem !important;
        font-weight: 600;
        line-height: 1;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.8125rem !important;
    }

    /* Typography - dark theme */
    h1 {
        color: #d8d9da;
        font-size: 1.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    h2 {
        color: #d8d9da;
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        letter-spacing: -0.01em;
    }
    h3 {
        color: #c4c7cc;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* Card container styling - dark panels */
    .element-container:has(> .stPlotlyChart) {
        background: #242629;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        border: 1px solid #2e3034;
    }

    /* Section subtitle */
    .section-subtitle {
        color: #9fa3a8;
        font-size: 0.875rem;
        font-weight: 400;
        margin-top: 0.25rem;
        margin-bottom: 2rem;
    }

    /* Remove default streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Custom divider - dark */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #2e3034;
    }

    /* Sidebar dark theme */
    [data-testid="stSidebar"] {
        background-color: #1f2226;
        border-right: 1px solid #2e3034;
    }
    [data-testid="stSidebar"] * {
        color: #d8d9da !important;
    }
    </style>
""", unsafe_allow_html=True)

GO_API = "https://ttc-alerts-api.vercel.app/api/go"

@st.cache_data(ttl=60)
def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data from {url}: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/GO_Transit_logo.svg/200px-GO_Transit_logo.svg.png", width=150)
    st.title("🚇 Navigation")
    st.markdown("---")

    st.markdown("### 📊 Pages")
    st.markdown("- **🏠 Home** (Current)")
    st.markdown("- **📈 Analytics**")
    st.markdown("- **🔍 Vehicle Tracker**")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=True)

    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("📡 **Data Source**")
    st.caption("• Metrolinx Open API")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# Header
st.title("GO Transit Command Center")
st.markdown(f"<p class='section-subtitle'>Real-time Operations Monitor • {datetime.now().strftime('%B %d, %Y at %H:%M EST')}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# NETWORK OVERVIEW - Hero Section
# ============================================================================
st.header("Network Overview")

# Metrics card container - dark panel
st.markdown("""
    <div style='background: #242629; border-radius: 8px; padding: 1.75rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 1px solid #2e3034; margin-bottom: 1.5rem;'>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

go_stats = fetch_data(f"{GO_API}?type=stats")
if go_stats and isinstance(go_stats, list) and len(go_stats) > 0:
    stats_dict = {i['metric']: i['value'] for i in go_stats}
else:
    st.warning("Unable to load GO Transit statistics")
    stats_dict = {}

if stats_dict:
    with col1:
        st.metric(
            "🚆 Performance",
            f"{stats_dict.get('Performance Rate', 0)}%",
            delta=f"{stats_dict.get('Performance Rate', 0) - 95}% vs target",
            delta_color="normal" if stats_dict.get('Performance Rate', 0) >= 95 else "inverse"
        )

    with col2:
        st.metric("🚊 Active Vehicles", stats_dict.get('Total Vehicles', 0),
                 delta=f"{stats_dict.get('Trains in Motion', 0) + stats_dict.get('Buses in Motion', 0)} moving")

    with col3:
        st.metric("✅ On Time", stats_dict.get('On Time', 0),
                 delta=f"{round(stats_dict.get('On Time', 0) / stats_dict.get('Total Vehicles', 1) * 100)}%")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GO TRANSIT SECTION
# ============================================================================
st.header("GO Transit Live Status")

go_stats = fetch_data(f"{GO_API}?type=stats")
if go_stats:
    stats_dict = {i['metric']: i['value'] for i in go_stats}

    # Performance Dashboard
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Performance Gauge - Dark Theme
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats_dict.get('Performance Rate', 0),
            title={'text': "On-Time Performance", 'font': {'size': 18, 'color': '#d8d9da'}},
            delta={'reference': 95, 'increasing': {'color': '#73bf69'}, 'decreasing': {'color': '#ff5705'}},
            number={'suffix': '%', 'font': {'size': 44, 'color': '#d8d9da'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#9fa3a8'},
                'bar': {'color': "#73bf69", 'thickness': 0.75},
                'bgcolor': "#1a1d21",
                'borderwidth': 1,
                'bordercolor': "#2e3034",
                'steps': [
                    {'range': [0, 70], 'color': '#3d2c2c'},
                    {'range': [70, 85], 'color': '#3d3420'},
                    {'range': [85, 95], 'color': '#2a3a2c'},
                    {'range': [95, 100], 'color': '#2f4f2f'}
                ],
                'threshold': {
                    'line': {'color': "#d8d9da", 'width': 3},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_gauge.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor='#242629',
            plot_bgcolor='#242629',
            font=dict(color='#d8d9da')
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Service Distribution - Dark Theme
        fig_fleet = go.Figure(data=[go.Pie(
            labels=['Trains', 'Buses'],
            values=[stats_dict.get('Trains Active', 0), stats_dict.get('Buses Active', 0)],
            hole=0.4,
            marker=dict(colors=['#73bf69', '#6e9bd1'], line=dict(color='#242629', width=2)),
            textinfo='label+value+percent',
            textfont=dict(size=14, color='#d8d9da'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig_fleet.update_layout(
            title={'text': 'Fleet Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#d8d9da'}},
            height=300,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color='#d8d9da')),
            paper_bgcolor='#242629',
            plot_bgcolor='#242629',
            font=dict(color='#d8d9da')
        )
        st.plotly_chart(fig_fleet, use_container_width=True)

    with col3:
        # On-Time vs Delayed - Dark Theme
        fig_status = go.Figure()

        fig_status.add_trace(go.Bar(
            x=['On Time', 'Delayed'],
            y=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
            marker=dict(
                color=['#73bf69', '#ff5705'],
                line=dict(color='#242629', width=1)
            ),
            text=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
            textposition='outside',
            textfont=dict(size=16, color='#d8d9da')
        ))

        fig_status.update_layout(
            title={'text': 'Service Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#d8d9da'}},
            height=300,
            yaxis=dict(title='Vehicles', color='#d8d9da', gridcolor='#2e3034'),
            xaxis=dict(color='#d8d9da'),
            showlegend=False,
            plot_bgcolor='#242629',
            paper_bgcolor='#242629',
            font=dict(color='#d8d9da'),
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col4:
        # Key Metrics
        st.metric("Total Vehicles", stats_dict.get('Total Vehicles', 0))
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Train Lines", stats_dict.get('Train Lines', 0))
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Bus Routes", stats_dict.get('Bus Routes', 0))

    # Time Series Trends - Dark Theme
    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    if go_timeseries:
        st.subheader("24-Hour Activity Trends")

        fig_ts = go.Figure()
        colors = ['#73bf69', '#6e9bd1', '#f5a742']

        for idx, series in enumerate(go_timeseries):
            timestamps = [datetime.fromtimestamp(p[1]/1000) for p in series['datapoints']]
            values = [p[0] for p in series['datapoints']]

            fig_ts.add_trace(go.Scatter(
                x=timestamps,
                y=values,
                mode='lines+markers',
                name=series['target'],
                line=dict(width=2, color=colors[idx % len(colors)]),
                marker=dict(size=5),
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x|%H:%M}<br>Value: %{y}<extra></extra>'
            ))

        fig_ts.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='#242629',
            paper_bgcolor='#242629',
            xaxis=dict(
                title=dict(text='Time', font=dict(color='#d8d9da')),
                showgrid=True,
                gridcolor='#2e3034',
                color='#d8d9da'
            ),
            yaxis=dict(
                title=dict(text='Count / Percentage', font=dict(color='#d8d9da')),
                showgrid=True,
                gridcolor='#2e3034',
                color='#d8d9da'
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='#d8d9da')
            ),
            font=dict(color='#d8d9da'),
            margin=dict(l=60, r=40, t=40, b=80)
        )

        st.plotly_chart(fig_ts, use_container_width=True)


# Footer - Dark Theme
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0; border-top: 1px solid #2e3034; margin-top: 2.5rem;'>
        <p style='color: #9fa3a8; font-size: 0.8125rem; margin: 0; font-weight: 500;'>
            Metrolinx Open API • Real-time GO Transit Data
        </p>
        <p style='color: #6e7175; font-size: 0.75rem; margin-top: 0.375rem;'>
            Last updated {} • Refreshes every 60s
        </p>
    </div>
""".format(datetime.now().strftime("%H:%M EST")), unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if time.time() - st.session_state.last_refresh > 60:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()
