import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Toronto Transit Live Dashboard",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stMetric {background-color: #f0f2f6; padding: 10px; border-radius: 5px;}
    h1 {color: #00853E; padding-bottom: 10px;}
    .ttc-section {border-left: 4px solid #DA291C;}
    .go-section {border-left: 4px solid #00853E;}
    </style>
    """, unsafe_allow_html=True)

# API Base URLs
GO_API = "https://ttc-alerts-api.vercel.app/api/go"
TTC_API = "https://ttc-alerts-api.vercel.app/api"

@st.cache_data(ttl=60)
def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Sidebar for transit system selection
with st.sidebar:
    st.title("🚇 Transit Dashboard")
    st.markdown("---")

    show_ttc = st.checkbox("Show TTC Data", value=True)
    show_go = st.checkbox("Show GO Transit Data", value=True)

    st.markdown("---")
    st.markdown("### Settings")
    auto_refresh = st.checkbox("Auto-refresh (60s)", value=True)

    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("📡 Live data from:")
    st.caption("• TTC GTFS-Realtime")
    st.caption("• Metrolinx Open API")

# Header
st.title("🚇 Toronto Transit - Live Dashboard")
st.caption("Real-time data for TTC & GO Transit • Greater Toronto Area")
current_time = datetime.now().strftime("%H:%M:%S EST • %Y-%m-%d")
st.markdown(f"**⏱️ {current_time}**")
st.markdown("---")

# ==============================================================================
# TTC SECTION
# ==============================================================================
if show_ttc:
    st.header("🚇 TTC - Toronto Transit Commission")

    ttc_alerts = fetch_data(f"{TTC_API}/alerts")
    ttc_summary = fetch_data(f"{TTC_API}/summary")

    if ttc_summary:
        # TTC Summary Metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        summary_dict = {item['metric']: item['value'] for item in ttc_summary}

        with col1:
            st.metric("Total Alerts", summary_dict.get('Total Alerts', 0))
        with col2:
            st.metric("Critical", summary_dict.get('Critical', 0))
        with col3:
            st.metric("High Severity", summary_dict.get('High Severity', 0))
        with col4:
            st.metric("Subway", summary_dict.get('Subway', 0))
        with col5:
            st.metric("Bus", summary_dict.get('Bus', 0))
        with col6:
            st.metric("Streetcar", summary_dict.get('Streetcar', 0))

    # TTC Service Disruptions Table
    if ttc_alerts:
        st.subheader("🚨 Current Service Disruptions")
        df_ttc = pd.DataFrame(ttc_alerts)

        # Limit to top 15
        df_ttc = df_ttc.head(15)

        # Color code by severity
        def highlight_severity(row):
            if row['Severity'] == 'High':
                return ['background-color: #f8d7da'] * len(row)
            elif row['Severity'] == 'Medium':
                return ['background-color: #fff3cd'] * len(row)
            else:
                return ['background-color: #d1ecf1'] * len(row)

        styled_ttc = df_ttc.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_ttc, use_container_width=True, height=400)

        # TTC Alert Type Distribution
        col1, col2 = st.columns(2)

        with col1:
            type_counts = df_ttc['Type'].value_counts()
            fig_ttc_type = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title='Alerts by Service Type',
                color_discrete_sequence=['#DA291C', '#0066CC', '#00853E']
            )
            st.plotly_chart(fig_ttc_type, use_container_width=True)

        with col2:
            severity_counts = df_ttc['Severity'].value_counts()
            fig_ttc_sev = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                title='Alerts by Severity',
                labels={'x': 'Severity', 'y': 'Count'},
                color=severity_counts.index,
                color_discrete_map={'High': 'red', 'Medium': 'orange', 'Low': 'green'}
            )
            st.plotly_chart(fig_ttc_sev, use_container_width=True)

    st.markdown("---")

# ==============================================================================
# GO TRANSIT SECTION
# ==============================================================================
if show_go:
    st.header("🚆 GO Transit - Metrolinx")

    go_stats = fetch_data(f"{GO_API}?type=stats")
    go_union = fetch_data(f"{GO_API}?type=union")
    go_lines_trains = fetch_data(f"{GO_API}?type=lines&vehicleType=trains")
    go_lines_buses = fetch_data(f"{GO_API}?type=lines&vehicleType=buses")
    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    go_vehicles = fetch_data(f"{GO_API}?type=vehicles")

    if go_stats:
        stats_dict = {item['metric']: item['value'] for item in go_stats}

        # GO Transit Key Metrics
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric("Performance", f"{stats_dict.get('Performance Rate', 0)}%",
                      delta=None if stats_dict.get('Performance Rate', 0) >= 95
                      else f"{stats_dict.get('Performance Rate', 0) - 100}%")
        with col2:
            st.metric("Total Vehicles", stats_dict.get('Total Vehicles', 0))
        with col3:
            st.metric("Trains Active", stats_dict.get('Trains Active', 0),
                      delta=f"{stats_dict.get('Trains in Motion', 0)} moving")
        with col4:
            st.metric("Buses Active", stats_dict.get('Buses Active', 0),
                      delta=f"{stats_dict.get('Buses in Motion', 0)} moving")
        with col5:
            st.metric("On Time", stats_dict.get('On Time', 0))
        with col6:
            st.metric("Delayed", stats_dict.get('Delayed', 0))

        # Performance Visualizations
        col1, col2, col3 = st.columns(3)

        with col1:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=stats_dict.get('Performance Rate', 0),
                title={'text': "On-Time Performance"},
                delta={'reference': 95},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightcoral"},
                        {'range': [70, 85], 'color': "lightyellow"},
                        {'range': [85, 95], 'color': "lightgreen"},
                        {'range': [95, 100], 'color': "green"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            status_df = pd.DataFrame([
                {'Status': 'On Time', 'Count': stats_dict.get('On Time', 0)},
                {'Status': 'Delayed', 'Count': stats_dict.get('Delayed', 0)}
            ])
            fig_status = px.bar(status_df, x='Status', y='Count',
                                title='Service Status',
                                color='Status',
                                color_discrete_map={'On Time': 'green', 'Delayed': 'red'},
                                text='Count')
            fig_status.update_traces(textposition='outside')
            st.plotly_chart(fig_status, use_container_width=True)

        with col3:
            vehicle_df = pd.DataFrame([
                {'Type': 'Trains', 'Count': stats_dict.get('Trains Active', 0)},
                {'Type': 'Buses', 'Count': stats_dict.get('Buses Active', 0)}
            ])
            fig_fleet = px.pie(vehicle_df, values='Count', names='Type',
                               title='Fleet Distribution',
                               color_discrete_sequence=['#00853E', '#0066CC'])
            st.plotly_chart(fig_fleet, use_container_width=True)

    # Time Series Trends
    if go_timeseries:
        st.subheader("📈 24-Hour Activity Trends")
        fig_ts = go.Figure()
        for series in go_timeseries:
            timestamps = [datetime.fromtimestamp(dp[1]/1000) for dp in series['datapoints']]
            values = [dp[0] for dp in series['datapoints']]
            fig_ts.add_trace(go.Scatter(x=timestamps, y=values,
                                        mode='lines', name=series['target']))
        fig_ts.update_layout(height=350, hovermode='x unified')
        st.plotly_chart(fig_ts, use_container_width=True)

    # Union Station & Train Lines
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚉 Union Station Departures")
        if go_union:
            df_union = pd.DataFrame(go_union)
            def color_union(val):
                if 'On Time' in str(val):
                    return 'background-color: #d4edda'
                elif 'Delayed' in str(val):
                    return 'background-color: #f8d7da'
                elif 'Early' in str(val):
                    return 'background-color: #d1ecf1'
                return ''
            styled_union = df_union.style.applymap(color_union, subset=['Status'])
            st.dataframe(styled_union, use_container_width=True, height=400)

    with col2:
        st.subheader("🚂 Train Lines Performance")
        if go_lines_trains:
            df_trains = pd.DataFrame(go_lines_trains)
            fig_trains = px.bar(df_trains, x='Line', y=['OnTime', 'Delayed'],
                                title='On Time vs Delayed', barmode='group',
                                color_discrete_map={'OnTime': 'green', 'Delayed': 'red'})
            st.plotly_chart(fig_trains, use_container_width=True)
            st.dataframe(df_trains, use_container_width=True, height=150)

    # Bus Routes Analysis
    st.subheader("🚌 Bus Routes Analysis")
    if go_lines_buses:
        df_buses = pd.DataFrame(go_lines_buses)

        col1, col2 = st.columns([2, 1])

        with col1:
            df_top20 = df_buses.nlargest(20, 'Total')
            fig_buses = go.Figure()
            fig_buses.add_trace(go.Bar(y=df_top20['Line'], x=df_top20['OnTime'],
                                       name='On Time', orientation='h',
                                       marker=dict(color='green')))
            fig_buses.add_trace(go.Bar(y=df_top20['Line'], x=df_top20['Delayed'],
                                       name='Delayed', orientation='h',
                                       marker=dict(color='red')))
            fig_buses.update_layout(barmode='stack', height=600,
                                   yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_buses, use_container_width=True)

        with col2:
            st.markdown("### 📊 Bus Statistics")
            st.metric("Total Routes", len(df_buses))
            st.metric("Total Buses", int(df_buses['Total'].sum()))
            st.metric("Avg per Route", f"{df_buses['Total'].mean():.1f}")
            busiest = df_buses.nlargest(1, 'Total').iloc[0]
            st.metric("Busiest Route", busiest['Line'],
                      delta=f"{busiest['Total']} buses")
            st.metric("Routes On-Time", len(df_buses[df_buses['Delayed'] == 0]))
            st.metric("Routes Delayed", len(df_buses[df_buses['Delayed'] > 0]))

    # Live Vehicle Map
    if go_vehicles and go_vehicles.get('vehicles'):
        st.subheader("🗺️ Live Vehicle Positions")
        df_vehicles = pd.DataFrame(go_vehicles['vehicles'])
        df_map = df_vehicles[(df_vehicles['Latitude'] != 0) &
                             (df_vehicles['Longitude'] != 0)]

        if not df_map.empty:
            col1, col2 = st.columns([3, 1])

            with col1:
                fig_map = px.scatter_mapbox(
                    df_map, lat="Latitude", lon="Longitude",
                    color="Type", hover_name="Display",
                    hover_data={"Status": True, "Line": True,
                               "Latitude": False, "Longitude": False},
                    color_discrete_map={"Train": "#00853E", "Bus": "#0066CC"},
                    zoom=8, height=500
                )
                fig_map.update_layout(mapbox_style="open-street-map",
                                     margin={"r": 0, "t": 0, "l": 0, "b": 0})
                st.plotly_chart(fig_map, use_container_width=True)

            with col2:
                st.markdown("### 📍 Vehicle Stats")
                st.metric("Tracked", len(df_map))
                st.metric("Trains", len(df_map[df_map['Type'] == 'Train']))
                st.metric("Buses", len(df_map[df_map['Type'] == 'Bus']))
                st.metric("Moving", len(df_map[df_map['IsInMotion'] == True]))
                st.metric("Stopped", len(df_map[df_map['IsInMotion'] == False]))
                delayed = len(df_map[df_map['Status'] == 'Delayed'])
                st.metric("Delayed", delayed)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("📡 TTC GTFS-RT • Metrolinx API")
with col2:
    st.caption("🔄 Auto-refresh: Every 60 seconds" if auto_refresh else "🔄 Manual refresh only")
with col3:
    st.caption(f"⚡ Powered by Streamlit")

# Auto-refresh
if auto_refresh:
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()

    if time.time() - st.session_state.last_refresh > 60:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()
