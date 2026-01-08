import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from route_data import get_route_name, get_station_name

# Page config
st.set_page_config(page_title="Toronto Transit Live", page_icon="🚇", layout="wide")

st.markdown("<style>.main {padding: 0rem 1rem;} .stMetric {background-color: #f0f2f6; padding: 10px; border-radius: 5px;} h1 {color: #00853E;}</style>", unsafe_allow_html=True)

GO_API = "https://ttc-alerts-api.vercel.app/api/go"
TTC_API = "https://ttc-alerts-api.vercel.app/api"

@st.cache_data(ttl=60)
def fetch_data(url):
    try:
        return requests.get(url, timeout=10).json()
    except:
        return None

# Sidebar
with st.sidebar:
    st.title("🚇 Controls")
    show_ttc = st.checkbox("TTC", value=True)
    show_go = st.checkbox("GO Transit", value=True)
    st.markdown("### 🔍 Vehicle Search")
    search_type = st.radio("", ["Trip #", "Route", "Off"])
    if search_type == "Trip #":
        trip_search = st.text_input("Trip number:")
    elif search_type == "Route":
        route_search = st.text_input("Route code:")
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

st.title("🚇 Toronto Transit Dashboard")
st.caption(f"⏱️ {datetime.now().strftime('%H:%M:%S EST • %Y-%m-%d')}")
st.markdown("---")

# Vehicle Search
go_vehicles = fetch_data(f"{GO_API}?type=vehicles")
if search_type != "Off" and go_vehicles and go_vehicles.get('vehicles'):
    df = pd.DataFrame(go_vehicles['vehicles'])
    if search_type == "Trip #" and 'trip_search' in locals() and trip_search:
        df = df[df['TripNumber'].astype(str).str.contains(trip_search, case=False)]
    elif search_type == "Route" and 'route_search' in locals() and route_search:
        df = df[df['Line'].str.upper() == route_search.upper()]

    if not df.empty:
        st.success(f"🔍 Found {len(df)} vehicle(s)")
        df['RouteName'] = df['Line'].apply(get_route_name)
        df_map = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]

        if not df_map.empty:
            fig = px.scatter_mapbox(df_map, lat="Latitude", lon="Longitude", color="Type",
                                   hover_name="Display", hover_data={"Status": True, "RouteName": True,
                                   "TripNumber": True, "Latitude": False, "Longitude": False},
                                   color_discrete_map={"Train": "#00853E", "Bus": "#0066CC"},
                                   zoom=10, height=350)
            fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df[['Type', 'TripNumber', 'RouteName', 'Display', 'Status', 'IsInMotion']], use_container_width=True)
        st.markdown("---")

# TTC
if show_ttc:
    st.header("🚇 TTC")
    ttc_summary = fetch_data(f"{TTC_API}/summary")
    if ttc_summary:
        cols = st.columns(6)
        d = {i['metric']: i['value'] for i in ttc_summary}
        for i, (k, v) in enumerate(d.items()):
            cols[i].metric(k, v)

    ttc_alerts = fetch_data(f"{TTC_API}/alerts")
    if ttc_alerts:
        df_ttc = pd.DataFrame(ttc_alerts).head(15)
        def hl(row):
            c = {'High': '#f8d7da', 'Medium': '#fff3cd', 'Low': '#d1ecf1'}
            return [f'background-color: {c.get(row["Severity"], "#fff")}'] * len(row)
        st.dataframe(df_ttc.style.apply(hl, axis=1), use_container_width=True, height=350)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(values=df_ttc['Type'].value_counts().values,
                                  names=df_ttc['Type'].value_counts().index,
                                  title='By Type'), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(x=df_ttc['Severity'].value_counts().index,
                                  y=df_ttc['Severity'].value_counts().values,
                                  title='By Severity'), use_container_width=True)
    st.markdown("---")

# GO Transit
if show_go:
    st.header("🚆 GO Transit")
    go_stats = fetch_data(f"{GO_API}?type=stats")
    if go_stats:
        d = {i['metric']: i['value'] for i in go_stats}
        cols = st.columns(6)
        cols[0].metric("Performance", f"{d.get('Performance Rate', 0)}%")
        cols[1].metric("Vehicles", d.get('Total Vehicles', 0))
        cols[2].metric("Trains", d.get('Trains Active', 0))
        cols[3].metric("Buses", d.get('Buses Active', 0))
        cols[4].metric("On Time", d.get('On Time', 0))
        cols[5].metric("Delayed", d.get('Delayed', 0))

        c1, c2, c3 = st.columns(3)
        with c1:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=d.get('Performance Rate', 0),
                          gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "blue"},
                          'steps': [{'range': [0,70], 'color': "lightcoral"},
                                   {'range': [70,85], 'color': "lightyellow"},
                                   {'range': [85,100], 'color': "lightgreen"}]}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(x=['On Time', 'Delayed'],
                                  y=[d.get('On Time', 0), d.get('Delayed', 0)],
                                  color=['On Time', 'Delayed'],
                                  color_discrete_map={'On Time': 'green', 'Delayed': 'red'}),
                           use_container_width=True)
        with c3:
            st.plotly_chart(px.pie(values=[d.get('Trains Active', 0), d.get('Buses Active', 0)],
                                  names=['Trains', 'Buses']), use_container_width=True)

    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    if go_timeseries:
        fig = go.Figure()
        for s in go_timeseries:
            fig.add_trace(go.Scatter(x=[datetime.fromtimestamp(p[1]/1000) for p in s['datapoints']],
                                    y=[p[0] for p in s['datapoints']], mode='lines', name=s['target']))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🚉 Union Station")
        go_union = fetch_data(f"{GO_API}?type=union")
        if go_union:
            df = pd.DataFrame(go_union)
            st.dataframe(df, use_container_width=True, height=350)

    with c2:
        st.subheader("🚂 Train Lines")
        go_trains = fetch_data(f"{GO_API}?type=lines&vehicleType=trains")
        if go_trains:
            df = pd.DataFrame(go_trains)
            df['LineName'] = df['Code'].apply(get_route_name)
            st.plotly_chart(px.bar(df, x='LineName', y=['OnTime', 'Delayed'],
                                  barmode='group'), use_container_width=True)
            st.dataframe(df[['LineName', 'Total', 'OnTime', 'Delayed']], use_container_width=True)

    st.subheader("🚌 Bus Routes")
    go_buses = fetch_data(f"{GO_API}?type=lines&vehicleType=buses")
    if go_buses:
        df = pd.DataFrame(go_buses)
        df['RouteName'] = df['Code'].apply(get_route_name)

        c1, c2 = st.columns([2, 1])
        with c1:
            top20 = df.nlargest(20, 'Total')
            fig = go.Figure()
            fig.add_trace(go.Bar(y=top20['RouteName'], x=top20['OnTime'], name='On Time',
                                orientation='h', marker=dict(color='green')))
            fig.add_trace(go.Bar(y=top20['RouteName'], x=top20['Delayed'], name='Delayed',
                                orientation='h', marker=dict(color='red')))
            fig.update_layout(barmode='stack', height=600, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.markdown("### 📊 Stats")
            st.metric("Routes", len(df))
            st.metric("Buses", int(df['Total'].sum()))
            busiest = df.nlargest(1, 'Total').iloc[0]
            st.metric("Busiest", busiest['Code'])
            st.caption(busiest['RouteName'])
            st.metric("On-Time Routes", len(df[df['Delayed'] == 0]))

        with st.expander("📋 All Routes"):
            search = st.text_input("Search:")
            if search:
                df = df[df['Code'].str.contains(search, case=False) | 
                       df['RouteName'].str.contains(search, case=False)]
            st.dataframe(df[['Code', 'RouteName', 'Total', 'OnTime', 'Delayed']],
                        use_container_width=True, height=400)

    if go_vehicles and go_vehicles.get('vehicles'):
        st.subheader("🗺️ Live Vehicles")
        df = pd.DataFrame(go_vehicles['vehicles'])
        df['RouteName'] = df['Line'].apply(get_route_name)
        df_map = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]

        if not df_map.empty:
            c1, c2 = st.columns([3, 1])
            with c1:
                fig = px.scatter_mapbox(df_map, lat="Latitude", lon="Longitude", color="Type",
                                       hover_name="Display", hover_data={"RouteName": True, "Status": True},
                                       color_discrete_map={"Train": "#00853E", "Bus": "#0066CC"},
                                       zoom=8, height=450)
                fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.metric("Tracked", len(df_map))
                st.metric("Trains", len(df_map[df_map['Type'] == 'Train']))
                st.metric("Buses", len(df_map[df_map['Type'] == 'Bus']))
                st.metric("Moving", len(df_map[df_map['IsInMotion'] == True]))

st.caption("📡 TTC GTFS-RT • Metrolinx API • ⚡ Streamlit")

if auto_refresh:
    if 'last' not in st.session_state:
        st.session_state.last = time.time()
    if time.time() - st.session_state.last > 60:
        st.session_state.last = time.time()
        st.cache_data.clear()
        st.rerun()
