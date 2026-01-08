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
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #00853E;
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
    st.caption("Real-time data from Metrolinx Open API • Greater Toronto Area")
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
timeseries_data = fetch_data("timeseries")
vehicles_data = fetch_data("vehicles")

if stats_data:
    # Convert stats to dictionary for easy access
    stats_dict = {item['metric']: item['value'] for item in stats_data}

    # === SECTION 1: Key Metrics ===
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
        st.metric("Trains Active", stats_dict.get('Trains Active', 0),
                  delta=f"{stats_dict.get('Trains in Motion', 0)} moving")

    with col4:
        st.metric("Buses Active", stats_dict.get('Buses Active', 0),
                  delta=f"{stats_dict.get('Buses in Motion', 0)} moving")

    with col5:
        st.metric("Train Lines", stats_dict.get('Train Lines', 0))

    with col6:
        st.metric("Bus Routes", stats_dict.get('Bus Routes', 0))

    st.markdown("---")

    # === SECTION 2: Performance Visualizations ===
    col1, col2, col3 = st.columns(3)

    with col1:
        # On-Time Performance Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=stats_dict.get('Performance Rate', 0),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "On-Time Performance", 'font': {'size': 20}},
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
            title='Service Status Breakdown',
            color='Status',
            color_discrete_map={'On Time': 'green', 'Delayed': 'red'},
            text='Count'
        )
        fig_bar.update_layout(height=300, showlegend=False)
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col3:
        # Train vs Bus Pie Chart
        vehicle_df = pd.DataFrame([
            {'Type': 'Trains', 'Count': stats_dict.get('Trains Active', 0)},
            {'Type': 'Buses', 'Count': stats_dict.get('Buses Active', 0)}
        ])
        fig_pie = px.pie(
            vehicle_df,
            values='Count',
            names='Type',
            title='Fleet Distribution',
            color='Type',
            color_discrete_map={'Trains': '#00853E', 'Buses': '#0066CC'}
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# === SECTION 3: Time Series Trends ===
if timeseries_data:
    st.subheader("📈 24-Hour Activity Trends")

    # Create time series figure
    fig_timeseries = go.Figure()

    for series in timeseries_data:
        target_name = series['target']
        datapoints = series['datapoints']

        timestamps = [datetime.fromtimestamp(dp[1]/1000) for dp in datapoints]
        values = [dp[0] for dp in datapoints]

        fig_timeseries.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines',
            name=target_name,
            line=dict(width=2)
        ))

    fig_timeseries.update_layout(
        height=400,
        xaxis_title="Time",
        yaxis_title="Count / Percentage",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_timeseries, use_container_width=True)

st.markdown("---")

# === SECTION 4: Union Station & Train Lines ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚉 Union Station - Next Departures")
    if union_data:
        df_union = pd.DataFrame(union_data)

        # Color code status
        def color_status(val):
            if 'On Time' in str(val):
                return 'background-color: #d4edda; color: #155724'
            elif 'Delayed' in str(val):
                return 'background-color: #f8d7da; color: #721c24'
            elif 'Early' in str(val):
                return 'background-color: #d1ecf1; color: #0c5460'
            return ''

        styled_df = df_union.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True, height=450)

        st.caption(f"📍 Showing next {len(df_union)} departures from Union Station")
    else:
        st.info("Loading Union Station departures...")

with col2:
    st.subheader("🚂 Train Lines Performance")
    if lines_trains:
        df_trains = pd.DataFrame(lines_trains)

        # Create performance bar chart
        fig_trains = px.bar(
            df_trains,
            x='Line',
            y=['OnTime', 'Delayed'],
            title='Train Lines - On Time vs Delayed',
            barmode='group',
            color_discrete_map={'OnTime': 'green', 'Delayed': 'red'},
            labels={'value': 'Vehicles', 'variable': 'Status'}
        )
        fig_trains.update_layout(height=300)
        st.plotly_chart(fig_trains, use_container_width=True)

        # Show detailed table
        st.dataframe(df_trains, use_container_width=True, height=120)
    else:
        st.info("Loading train lines data...")

st.markdown("---")

# === SECTION 5: Bus Routes Analysis ===
st.subheader("🚌 Bus Routes Performance Analysis")

if lines_buses:
    df_buses = pd.DataFrame(lines_buses)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Top 20 busiest routes horizontal bar
        df_buses_top = df_buses.nlargest(20, 'Total')

        fig_buses = go.Figure()
        fig_buses.add_trace(go.Bar(
            y=df_buses_top['Line'],
            x=df_buses_top['OnTime'],
            name='On Time',
            orientation='h',
            marker=dict(color='green')
        ))
        fig_buses.add_trace(go.Bar(
            y=df_buses_top['Line'],
            x=df_buses_top['Delayed'],
            name='Delayed',
            orientation='h',
            marker=dict(color='red')
        ))

        fig_buses.update_layout(
            barmode='stack',
            title='Top 20 Busiest Bus Routes - Service Status',
            height=600,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title='Number of Buses',
            yaxis_title='Route'
        )
        st.plotly_chart(fig_buses, use_container_width=True)

    with col2:
        st.markdown("### 📊 Bus Route Statistics")

        total_routes = len(df_buses)
        total_buses = df_buses['Total'].sum()
        avg_per_route = df_buses['Total'].mean()
        busiest_route = df_buses.nlargest(1, 'Total').iloc[0]

        st.metric("Total Routes Operating", total_routes)
        st.metric("Total Buses Active", int(total_buses))
        st.metric("Average Buses/Route", f"{avg_per_route:.1f}")
        st.metric("Busiest Route", busiest_route['Line'],
                  delta=f"{busiest_route['Total']} buses")

        # Performance summary
        routes_ontime = len(df_buses[df_buses['Delayed'] == 0])
        routes_delayed = len(df_buses[df_buses['Delayed'] > 0])

        st.markdown("### 🎯 Route Performance")
        st.metric("Routes 100% On-Time", routes_ontime)
        st.metric("Routes with Delays", routes_delayed)

    # Show full table with filters
    with st.expander("📋 View All Bus Routes Data (Full Table)"):
        st.dataframe(df_buses.sort_values('Total', ascending=False),
                     use_container_width=True, height=400)

else:
    st.info("Loading bus routes data...")

st.markdown("---")

# === SECTION 6: Live Vehicle Tracking ===
if vehicles_data and vehicles_data.get('vehicles'):
    st.subheader("🗺️ Live Vehicle Positions")

    vehicles = vehicles_data['vehicles']
    df_vehicles = pd.DataFrame(vehicles)

    # Filter vehicles with valid coordinates
    df_map = df_vehicles[(df_vehicles['Latitude'] != 0) & (df_vehicles['Longitude'] != 0)]

    if not df_map.empty:
        col1, col2 = st.columns([3, 1])

        with col1:
            # Create map
            fig_map = px.scatter_mapbox(
                df_map,
                lat="Latitude",
                lon="Longitude",
                color="Type",
                hover_name="Display",
                hover_data={
                    "Status": True,
                    "Line": True,
                    "TripNumber": True,
                    "Latitude": False,
                    "Longitude": False
                },
                color_discrete_map={"Train": "#00853E", "Bus": "#0066CC"},
                zoom=8,
                height=500
            )

            fig_map.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )

            st.plotly_chart(fig_map, use_container_width=True)

        with col2:
            st.markdown("### 📍 Vehicle Stats")
            st.metric("Vehicles Tracked", len(df_map))
            st.metric("Trains on Map", len(df_map[df_map['Type'] == 'Train']))
            st.metric("Buses on Map", len(df_map[df_map['Type'] == 'Bus']))

            in_motion = len(df_map[df_map['IsInMotion'] == True])
            stopped = len(df_map) - in_motion
            st.metric("Vehicles Moving", in_motion)
            st.metric("Vehicles Stopped", stopped)

            delayed_vehicles = len(df_map[df_map['Status'] == 'Delayed'])
            st.metric("Delayed Vehicles", delayed_vehicles,
                      delta=f"{(delayed_vehicles/len(df_map)*100):.1f}%")

    else:
        st.info("No vehicle position data available at this time.")

st.markdown("---")

# === SECTION 7: Detailed Statistics Tables ===
with st.expander("📊 Detailed Network Statistics"):
    if stats_data:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### All System Metrics")
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)

        with col2:
            st.markdown("### Performance Breakdown")
            perf_data = [
                {"Metric": "Total Vehicles", "Value": stats_dict.get('Total Vehicles', 0)},
                {"Metric": "Vehicles On Time", "Value": stats_dict.get('On Time', 0)},
                {"Metric": "Vehicles Delayed", "Value": stats_dict.get('Delayed', 0)},
                {"Metric": "Performance Rate", "Value": f"{stats_dict.get('Performance Rate', 0)}%"},
                {"Metric": "Trains in Motion", "Value": stats_dict.get('Trains in Motion', 0)},
                {"Metric": "Buses in Motion", "Value": stats_dict.get('Buses in Motion', 0)},
            ]
            df_perf = pd.DataFrame(perf_data)
            st.dataframe(df_perf, use_container_width=True)

# Footer
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.caption("📡 Live data from Metrolinx Open API")
with col2:
    st.caption("🔄 Auto-refresh: Every 60 seconds")
with col3:
    st.caption(f"⚡ Powered by Streamlit")
with col4:
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.caption(f"🕐 Last update: {last_update}")

# Auto-refresh every 60 seconds
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = current_time
    st.cache_data.clear()
    st.rerun()
