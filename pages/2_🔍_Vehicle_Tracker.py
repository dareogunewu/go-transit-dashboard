"""
GO Transit Vehicle Tracker - Live Vehicle Monitoring
Advanced search and tracking for trains and buses
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from route_data import get_route_name

st.set_page_config(page_title="Vehicle Tracker", page_icon="🔍", layout="wide")

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
    }

    .stApp {
        background-color: #181b1f;
    }

    .stMetric {
        background: #242629;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #2e3034;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    .stMetric:hover {
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
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
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #2e3034;
    }
    h3 {
        color: #c4c7cc;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    .section-subtitle {
        color: #9fa3a8;
        font-size: 0.875rem;
        font-weight: 400;
        margin-top: 0.25rem;
        margin-bottom: 2rem;
    }

    .element-container:has(> .stPlotlyChart) {
        background: #242629;
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
        border: 1px solid #2e3034;
    }

    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #2e3034;
    }

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
        return requests.get(url, timeout=10).json()
    except:
        return None

# Header
st.title("GO Transit Vehicle Tracker")
st.markdown(f"<p class='section-subtitle'>Live Vehicle Monitoring & Advanced Search • {datetime.now().strftime('%B %d, %Y at %H:%M EST')}</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar Search Controls
with st.sidebar:
    st.markdown("### 🔍 Search Options")

    search_mode = st.radio(
        "Search by:",
        ["🚂 Route Code", "🎫 Trip Number", "📍 Location", "🚦 Status", "📊 Show All"],
        index=4
    )

    st.markdown("---")

    if search_mode == "🚂 Route Code":
        route_input = st.text_input("Enter route code (e.g., LW, 41, 56):")
        route_input = route_input.upper().strip() if route_input else ""

    elif search_mode == "🎫 Trip Number":
        trip_input = st.text_input("Enter trip number:")
        trip_input = trip_input.strip() if trip_input else ""

    elif search_mode == "🚦 Status":
        status_filter = st.selectbox(
            "Select status:",
            ["All Statuses", "On Time", "Delayed", "Early"]
        )

    st.markdown("---")
    st.markdown("### 🎛️ Filters")

    vehicle_type = st.multiselect(
        "Vehicle Type:",
        ["Train", "Bus"],
        default=["Train", "Bus"]
    )

    show_moving_only = st.checkbox("Moving vehicles only", value=False)
    show_map = st.checkbox("Show map", value=True)

    st.markdown("---")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"🕐 Last update: {datetime.now().strftime('%H:%M:%S')}")

# Fetch vehicle data
go_vehicles = fetch_data(f"{GO_API}?type=vehicles")

if not go_vehicles or not go_vehicles.get('vehicles'):
    st.error("Unable to fetch vehicle data. Please try again.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(go_vehicles['vehicles'])
df['RouteName'] = df['Line'].apply(get_route_name)

# Apply filters
original_count = len(df)

# Vehicle type filter
if vehicle_type:
    df = df[df['Type'].isin(vehicle_type)]

# Motion filter
if show_moving_only:
    df = df[df['IsInMotion'] == True]

# Search mode filters
if search_mode == "🚂 Route Code" and route_input:
    df = df[df['Line'].str.upper() == route_input]

elif search_mode == "🎫 Trip Number" and trip_input:
    df = df[df['TripNumber'].astype(str).str.contains(trip_input, case=False)]

elif search_mode == "🚦 Status" and status_filter != "All Statuses":
    df = df[df['Status'].str.contains(status_filter, case=False)]

elif search_mode == "📍 Location":
    # Location-based search (lat/lon bounds)
    st.sidebar.markdown("### 📍 Location Bounds")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        min_lat = st.sidebar.number_input("Min Latitude", value=43.0, format="%.4f")
        min_lon = st.sidebar.number_input("Min Longitude", value=-80.0, format="%.4f")
    with col2:
        max_lat = st.sidebar.number_input("Max Latitude", value=44.0, format="%.4f")
        max_lon = st.sidebar.number_input("Max Longitude", value=-78.0, format="%.4f")

    df = df[
        (df['Latitude'] >= min_lat) &
        (df['Latitude'] <= max_lat) &
        (df['Longitude'] >= min_lon) &
        (df['Longitude'] <= max_lon)
    ]

# Filter out vehicles with no location
df_with_location = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]

# Summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🔍 Found", len(df), delta=f"{len(df) - original_count} filtered")

with col2:
    trains_count = len(df[df['Type'] == 'Train'])
    st.metric("🚂 Trains", trains_count)

with col3:
    buses_count = len(df[df['Type'] == 'Bus'])
    st.metric("🚌 Buses", buses_count)

with col4:
    moving_count = len(df[df['IsInMotion'] == True])
    st.metric("🚦 Moving", moving_count)

with col5:
    on_time_count = len(df[df['Status'].str.contains('On Time', case=False, na=False)])
    st.metric("✅ On Time", on_time_count)

st.markdown("---")

# Map View
if show_map and not df_with_location.empty:
    st.subheader("🗺️ Live Vehicle Map")

    # Calculate map center
    center_lat = df_with_location['Latitude'].mean()
    center_lon = df_with_location['Longitude'].mean()

    # Determine zoom level based on spread
    lat_range = df_with_location['Latitude'].max() - df_with_location['Latitude'].min()
    lon_range = df_with_location['Longitude'].max() - df_with_location['Longitude'].min()
    max_range = max(lat_range, lon_range)

    if max_range < 0.1:
        zoom = 12
    elif max_range < 0.5:
        zoom = 10
    elif max_range < 1.0:
        zoom = 9
    else:
        zoom = 8

    # Create map - Dark Theme
    fig_map = px.scatter_mapbox(
        df_with_location,
        lat="Latitude",
        lon="Longitude",
        color="Type",
        size=[10] * len(df_with_location),
        hover_name="Display",
        hover_data={
            "RouteName": True,
            "TripNumber": True,
            "Status": True,
            "IsInMotion": True,
            "Latitude": ":.4f",
            "Longitude": ":.4f"
        },
        color_discrete_map={"Train": "#73bf69", "Bus": "#6e9bd1"},
        zoom=zoom,
        height=500
    )

    fig_map.update_layout(
        mapbox_style="streets",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_color="#0f172a"),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff'
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

# Statistics Dashboard
if not df.empty:
    st.subheader("📊 Fleet Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Status Distribution - Dark Theme
        status_counts = df['Status'].value_counts()

        fig_status = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker=dict(
                colors=['#73bf69' if 'On Time' in str(s) else '#ff5705' if 'Delay' in str(s) else '#f5a742' for s in status_counts.index]
            ),
            textinfo='label+value+percent',
            textfont=dict(size=14, color='#d8d9da')
        )])

        fig_status.update_layout(
            title={'text': 'Status Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#d8d9da'}},
            height=300,
            paper_bgcolor='#242629',
            plot_bgcolor='#242629',
            font=dict(color='#d8d9da')
        )

        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Motion Status - Dark Theme
        motion_data = df['IsInMotion'].value_counts()

        fig_motion = go.Figure(data=[go.Bar(
            x=['Moving', 'Stopped'],
            y=[motion_data.get(True, 0), motion_data.get(False, 0)],
            marker=dict(color=['#73bf69', '#6e9bd1']),
            text=[motion_data.get(True, 0), motion_data.get(False, 0)],
            textposition='outside',
            textfont=dict(size=16, color='#d8d9da')
        )])

        fig_motion.update_layout(
            title={'text': 'Motion Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#d8d9da'}},
            height=300,
            yaxis=dict(title='Count', color='#d8d9da', gridcolor='#2e3034'),
            xaxis=dict(color='#d8d9da'),
            showlegend=False,
            paper_bgcolor='#242629',
            plot_bgcolor='#242629',
            font=dict(color='#d8d9da')
        )

        st.plotly_chart(fig_motion, use_container_width=True)

    with col3:
        # Top 5 Routes - Dark Theme
        route_counts = df['RouteName'].value_counts().head(5)

        fig_routes = go.Figure(data=[go.Bar(
            y=route_counts.index,
            x=route_counts.values,
            orientation='h',
            marker=dict(
                color=route_counts.values,
                colorscale=[[0, '#2e3034'], [0.5, '#6e9bd1'], [1, '#73bf69']],
                showscale=False
            ),
            text=route_counts.values,
            textposition='outside',
            textfont=dict(size=14, color='#d8d9da')
        )])

        fig_routes.update_layout(
            title={'text': 'Top 5 Active Routes', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#d8d9da'}},
            height=300,
            xaxis=dict(title='Vehicles', color='#d8d9da', gridcolor='#2e3034'),
            yaxis=dict(categoryorder='total ascending', color='#d8d9da'),
            paper_bgcolor='#242629',
            plot_bgcolor='#242629',
            font=dict(color='#d8d9da')
        )

        st.plotly_chart(fig_routes, use_container_width=True)

    st.markdown("---")

# Vehicle Data Table
if not df.empty:
    st.subheader("📋 Vehicle Details")

    # Add sorting options
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["TripNumber", "RouteName", "Status", "Type"],
            index=0
        )

    with col2:
        sort_order = st.radio("Order:", ["Ascending", "Descending"], horizontal=True)

    # Sort dataframe
    df_display = df.sort_values(
        by=sort_by,
        ascending=(sort_order == "Ascending")
    )

    # Select columns to display
    display_columns = ['Type', 'TripNumber', 'RouteName', 'Display', 'Status', 'IsInMotion']

    if 'Latitude' in df_display.columns and 'Longitude' in df_display.columns:
        display_columns.extend(['Latitude', 'Longitude'])

    # Style the dataframe
    def highlight_status(row):
        if 'On Time' in str(row['Status']):
            color = '#c8e6c9'  # Light green
        elif 'Delay' in str(row['Status']):
            color = '#ffcdd2'  # Light red
        elif 'Early' in str(row['Status']):
            color = '#fff9c4'  # Light yellow
        else:
            color = '#ffffff'  # White

        return [f'background-color: {color}'] * len(row)

    # Display styled dataframe
    styled_df = df_display[display_columns].style.apply(highlight_status, axis=1)

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )

    # Download option
    csv = df_display.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"go_transit_vehicles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ No vehicles found matching your search criteria.")
    st.info("💡 Try adjusting your filters or search parameters.")

# Footer - Dark Theme
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0; border-top: 1px solid #2e3034; margin-top: 2.5rem;'>
        <p style='color: #9fa3a8; font-size: 0.8125rem; margin: 0; font-weight: 500;'>
            Real-time GPS tracking • Metrolinx Open API
        </p>
        <p style='color: #6e7175; font-size: 0.75rem; margin-top: 0.375rem;'>
            Data refreshes every 60 seconds
        </p>
    </div>
""", unsafe_allow_html=True)
