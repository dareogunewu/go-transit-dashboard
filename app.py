import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="GO Transit Live Dashboard",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #00853E;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# API Base URL
API_BASE = "https://ttc-alerts-api.vercel.app/api/go"

@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_data(endpoint):
    """Fetch data from API with error handling"""
    try:
        response = requests.get(f"{API_BASE}?type={endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching {endpoint}: {str(e)}")
        return None

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚆 GO Transit - Live Service Dashboard")
with col2:
    current_time = datetime.now().strftime("%H:%M:%S EST")
    st.markdown(f"### ⏱️ {current_time}")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# Fetch all data
stats_data = fetch_data("stats")
union_data = fetch_data("union")
lines_trains = fetch_data("lines&vehicleType=trains")
lines_buses = fetch_data("lines&vehicleType=buses")

if stats_data:
    # Convert stats to dictionary for easy access
    stats_dict = {item['metric']: item['value'] for item in stats_data}

    # Top Row - Key Metrics
    st.subheader("📊 Network Overview")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Network Performance",
            f"{stats_dict.get('Performance Rate', 0)}%",
            delta=None if stats_dict.get('Performance Rate', 0) >= 95 else f"{stats_dict.get('Performance Rate', 0) - 100}%"
        )

    with col2:
        st.metric("Total Vehicles", stats_dict.get('Total Vehicles', 0))

    with col3:
        st.metric("Trains Active", stats_dict.get('Trains Active', 0), delta=f"{stats_dict.get('Trains in Motion', 0)} moving")

    with col4:
        st.metric("Buses Active", stats_dict.get('Buses Active', 0), delta=f"{stats_dict.get('Buses in Motion', 0)} moving")

    with col5:
        st.metric("Train Lines", stats_dict.get('Train Lines', 0))

    with col6:
        st.metric("Bus Routes", stats_dict.get('Bus Routes', 0))

    st.markdown("---")

    # Second Row - Performance Stats
    col1, col2 = st.columns(2)

    with col1:
        # On-Time Performance Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats_dict.get('Performance Rate', 0),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "On-Time Performance", 'font': {'size': 24}},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightcoral"},
                    {'range': [70, 85], 'color': "lightyellow"},
                    {'range': [85, 95], 'color': "lightgreen"},
                    {'range': [95, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Service Status Bar Chart
        status_df = pd.DataFrame([
            {'Status': 'On Time', 'Count': stats_dict.get('On Time', 0)},
            {'Status': 'Delayed', 'Count': stats_dict.get('Delayed', 0)}
        ])
        fig_bar = px.bar(
            status_df,
            x='Status',
            y='Count',
            title='Service Status',
            color='Status',
            color_discrete_map={'On Time': 'green', 'Delayed': 'red'}
        )
        fig_bar.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Third Row - Tables
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚉 Union Station - Next Departures")
    if union_data:
        df_union = pd.DataFrame(union_data)

        # Color code status
        def color_status(val):
            if 'On Time' in str(val):
                return 'background-color: #d4edda'
            elif 'Delayed' in str(val):
                return 'background-color: #f8d7da'
            elif 'Early' in str(val):
                return 'background-color: #d1ecf1'
            return ''

        styled_df = df_union.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("Loading Union Station departures...")

with col2:
    st.subheader("🚂 Train Lines Performance")
    if lines_trains:
        df_trains = pd.DataFrame(lines_trains)
        st.dataframe(df_trains, use_container_width=True, height=400)
    else:
        st.info("Loading train lines data...")

st.markdown("---")

# Fourth Row - Bus Routes
st.subheader("🚌 Top Bus Routes Performance")
if lines_buses:
    df_buses = pd.DataFrame(lines_buses)

    # Show top 15 busiest routes
    df_buses_top = df_buses.nlargest(15, 'Total')

    # Create horizontal bar chart
    fig_buses = px.bar(
        df_buses_top,
        y='Line',
        x='Total',
        title='Top 15 Busiest Bus Routes',
        orientation='h',
        color='OnTime',
        color_continuous_scale='RdYlGn'
    )
    fig_buses.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_buses, use_container_width=True)

    # Show full table with filters
    with st.expander("📋 View All Bus Routes Data"):
        st.dataframe(df_buses, use_container_width=True)
else:
    st.info("Loading bus routes data...")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📡 Live data from Metrolinx Open API")
with col2:
    st.caption(f"🔄 Auto-refresh: Every 60 seconds")
with col3:
    st.caption(f"⚡ Powered by Streamlit")

# Auto-refresh every 60 seconds
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = current_time
    st.cache_data.clear()
    st.rerun()
