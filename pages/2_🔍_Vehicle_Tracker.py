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

# Bright Modern Theme (matches main app)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        padding: 1.5rem 2rem !important;
        max-width: 1600px;
        margin: 0 auto;
    }

    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
    }

    .stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%) !important;
        border: 2px solid #e0e7ff !important;
        border-radius: 16px !important;
        padding: 1.25rem 1rem !important;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 120px;
    }
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.25) !important;
        border-color: #3b82f6 !important;
    }
    .stMetric label {
        color: #6366f1 !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 0.5rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
    }

    h1 {
        color: #0f172a;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h2 {
        color: #1e293b;
        font-size: 1.75rem;
        font-weight: 800;
        margin: 3rem 0 1.5rem 0;
        position: relative;
        padding-bottom: 1rem;
    }
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 80px;
        height: 5px;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 3px;
    }
    h3 {
        color: #334155;
        font-size: 1.125rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .section-subtitle {
        color: #64748b;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.3px;
    }

    .element-container:has(> .stPlotlyChart) {
        background: #ffffff;
        border: 2px solid #e0e7ff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
    }
    .element-container:has(> .stPlotlyChart):hover {
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        border-color: #c7d2fe;
        transform: translateY(-2px);
    }

    hr {
        margin: 3rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        opacity: 0.4;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid #e0e7ff;
        box-shadow: 4px 0 24px rgba(99, 102, 241, 0.1);
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
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

    # Create map - Bright Theme
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
        color_discrete_map={"Train": "#10b981", "Bus": "#3b82f6"},
        zoom=zoom,
        height=500,
        center={"lat": center_lat, "lon": center_lon}
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
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
        # Status Distribution - Bright Theme
        status_counts = df['Status'].value_counts()

        fig_status = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker=dict(
                colors=['#10b981' if 'On Time' in str(s) else '#ef4444' if 'Delay' in str(s) else '#f59e0b' for s in status_counts.index]
            ),
            textinfo='label+value+percent',
            textfont=dict(size=14, color='#1e293b', family='Plus Jakarta Sans', weight=600)
        )])

        fig_status.update_layout(
            title={'text': 'Status Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#1e293b', 'family': 'Plus Jakarta Sans'}},
            height=300,
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans')
        )

        st.plotly_chart(fig_status, use_container_width=True)

    with col2:
        # Motion Status - Bright Theme
        motion_data = df['IsInMotion'].value_counts()

        fig_motion = go.Figure(data=[go.Bar(
            x=['Moving', 'Stopped'],
            y=[motion_data.get(True, 0), motion_data.get(False, 0)],
            marker=dict(color=['#10b981', '#3b82f6']),
            text=[motion_data.get(True, 0), motion_data.get(False, 0)],
            textposition='outside',
            textfont=dict(size=16, color='#0f172a', family='Plus Jakarta Sans', weight=700)
        )])

        fig_motion.update_layout(
            title={'text': 'Motion Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#1e293b', 'family': 'Plus Jakarta Sans'}},
            height=300,
            yaxis=dict(title='Count', color='#64748b', gridcolor='#e2e8f0', tickfont=dict(color='#334155', family='Plus Jakarta Sans')),
            xaxis=dict(color='#334155', tickfont=dict(color='#334155', family='Plus Jakarta Sans')),
            showlegend=False,
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans')
        )

        st.plotly_chart(fig_motion, use_container_width=True)

    with col3:
        # Top 5 Routes - Bright Theme
        route_counts = df['RouteName'].value_counts().head(5)

        fig_routes = go.Figure(data=[go.Bar(
            y=route_counts.index,
            x=route_counts.values,
            orientation='h',
            marker=dict(
                color=route_counts.values,
                colorscale=[[0, '#dbeafe'], [0.5, '#3b82f6'], [1, '#1e40af']],
                showscale=False
            ),
            text=route_counts.values,
            textposition='outside',
            textfont=dict(size=14, color='#0f172a', family='Plus Jakarta Sans', weight=600)
        )])

        fig_routes.update_layout(
            title={'text': 'Top 5 Active Routes', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 18, 'color': '#1e293b', 'family': 'Plus Jakarta Sans'}},
            height=300,
            xaxis=dict(title='Vehicles', color='#64748b', gridcolor='#e2e8f0', tickfont=dict(color='#334155', family='Plus Jakarta Sans')),
            yaxis=dict(categoryorder='total ascending', color='#334155', tickfont=dict(color='#334155', family='Plus Jakarta Sans')),
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans')
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

# Footer - Bright Theme
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2.5rem 0; margin-top: 3rem;
    background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
    border-top: 3px solid #3b82f6;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);'>
        <div style='color: #1e40af; font-size: 0.875rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.75rem;'>
            🗺️ LIVE GPS TRACKING
        </div>
        <div style='color: #475569; font-size: 0.875rem; font-weight: 600;'>
            Real-time vehicle positions • Metrolinx Open API
        </div>
        <div style='color: #64748b; font-size: 0.8rem; margin-top: 0.75rem;'>
            🔄 Data refreshes every 60 seconds
        </div>
    </div>
""", unsafe_allow_html=True)
