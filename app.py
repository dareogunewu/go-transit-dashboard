"""
Toronto Transit Dashboard - Home Page
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
    page_title="Toronto Transit Dashboard",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom theme
st.markdown("""
    <style>
    .main {padding: 0rem 1rem;}
    .stMetric {
        background: linear-gradient(135deg, #0066CC 0%, #0080FF 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stMetric label {color: rgba(255,255,255,0.9) !important; font-weight: 600;}
    .stMetric [data-testid="stMetricValue"] {color: white !important; font-size: 2rem !important;}
    h1 {
        background: linear-gradient(135deg, #0066CC 0%, #1E90FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-left: 5px solid #0066CC;
    }
    </style>
""", unsafe_allow_html=True)

GO_API = "https://ttc-alerts-api.vercel.app/api/go"
TTC_API = "https://ttc-alerts-api.vercel.app/api"

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
    show_ttc = st.checkbox("Show TTC", value=True)
    show_go = st.checkbox("Show GO Transit", value=True)

    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("📡 **Data Sources**")
    st.caption("• TTC GTFS-Realtime")
    st.caption("• Metrolinx Open API")
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚇 Toronto Transit Command Center")
    st.markdown("### Real-time monitoring for TTC & GO Transit • Greater Toronto Area")
with col2:
    st.metric("System Status", "🟢 OPERATIONAL", delta="All Systems Online")

st.markdown("---")

# ============================================================================
# NETWORK OVERVIEW - Hero Section
# ============================================================================
st.header("📊 Network Overview")

col1, col2, col3, col4, col5 = st.columns(5)

if show_go:
    go_stats = fetch_data(f"{GO_API}?type=stats")
    if go_stats and isinstance(go_stats, list) and len(go_stats) > 0:
        stats_dict = {i['metric']: i['value'] for i in go_stats}
    else:
        st.warning("Unable to load GO Transit statistics")
        stats_dict = {}

    if stats_dict:
        with col1:
            st.metric(
                "🚆 GO Performance",
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

if show_ttc:
    ttc_summary = fetch_data(f"{TTC_API}/summary")
    if ttc_summary:
        summary_dict = {i['metric']: i['value'] for i in ttc_summary}

        with col4:
            st.metric("🚨 TTC Alerts", summary_dict.get('Total Alerts', 0),
                     delta=f"{summary_dict.get('Critical', 0)} critical",
                     delta_color="inverse" if summary_dict.get('Critical', 0) > 0 else "off")

        with col5:
            total_services = summary_dict.get('Subway', 0) + summary_dict.get('Bus', 0) + summary_dict.get('Streetcar', 0)
            st.metric("🚇 TTC Services", total_services,
                     delta=f"{summary_dict.get('Subway', 0)} subway")

st.markdown("---")

# ============================================================================
# GO TRANSIT SECTION
# ============================================================================
if show_go:
    st.header("🚆 GO Transit Live Status")

    go_stats = fetch_data(f"{GO_API}?type=stats")
    if go_stats:
        stats_dict = {i['metric']: i['value'] for i in go_stats}

        # Performance Dashboard
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Performance Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=stats_dict.get('Performance Rate', 0),
                title={'text': "On-Time Performance", 'font': {'size': 24, 'color': '#0066CC'}},
                delta={'reference': 95, 'increasing': {'color': '#0066CC'}},
                number={'suffix': '%', 'font': {'size': 48}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 2},
                    'bar': {'color': "#0066CC", 'thickness': 0.8},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 70], 'color': '#ffebee'},
                        {'range': [70, 85], 'color': '#fff9c4'},
                        {'range': [85, 95], 'color': '#e8f5e9'},
                        {'range': [95, 100], 'color': '#c8e6c9'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col2:
            # Service Distribution
            fig_fleet = go.Figure(data=[go.Pie(
                labels=['Trains', 'Buses'],
                values=[stats_dict.get('Trains Active', 0), stats_dict.get('Buses Active', 0)],
                hole=0.4,
                marker=dict(colors=['#0066CC', '#1E90FF'], line=dict(color='white', width=2)),
                textinfo='label+value+percent',
                textfont=dict(size=14, color='white'),
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            fig_fleet.update_layout(
                title={'text': 'Fleet Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_fleet, use_container_width=True)

        with col3:
            # On-Time vs Delayed
            fig_status = go.Figure()

            fig_status.add_trace(go.Bar(
                x=['On Time', 'Delayed'],
                y=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
                marker=dict(
                    color=['#0066CC', '#1E90FF'],
                    line=dict(color='white', width=2)
                ),
                text=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
                textposition='outside',
                textfont=dict(size=16)
            ))

            fig_status.update_layout(
                title={'text': 'Service Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
                height=300,
                yaxis_title='Vehicles',
                showlegend=False,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            st.plotly_chart(fig_status, use_container_width=True)

        with col4:
            # Key Metrics Cards
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Vehicles", stats_dict.get('Total Vehicles', 0))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="metric-card" style="margin-top:10px;">', unsafe_allow_html=True)
            st.metric("Train Lines", stats_dict.get('Train Lines', 0))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="metric-card" style="margin-top:10px;">', unsafe_allow_html=True)
            st.metric("Bus Routes", stats_dict.get('Bus Routes', 0))
            st.markdown('</div>', unsafe_allow_html=True)

    # Time Series Trends
    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    if go_timeseries:
        st.subheader("📈 24-Hour Activity Trends")

        fig_ts = go.Figure()
        colors = ['#0066CC', '#1E90FF', '#4169E1']

        for idx, series in enumerate(go_timeseries):
            timestamps = [datetime.fromtimestamp(p[1]/1000) for p in series['datapoints']]
            values = [p[0] for p in series['datapoints']]

            fig_ts.add_trace(go.Scatter(
                x=timestamps,
                y=values,
                mode='lines+markers',
                name=series['target'],
                line=dict(width=3, color=colors[idx % len(colors)]),
                marker=dict(size=6),
                fill='tonexty' if idx > 0 else None,
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x|%H:%M}<br>Value: %{y}<extra></extra>'
            ))

        fig_ts.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0.02)',
            xaxis=dict(title='Time', showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(title='Count / Percentage', showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=60, r=40, t=40, b=80)
        )

        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

# ============================================================================
# TTC SECTION
# ============================================================================
if show_ttc:
    st.header("🚇 TTC Service Status")

    ttc_alerts = fetch_data(f"{TTC_API}/alerts")
    ttc_summary = fetch_data(f"{TTC_API}/summary")

    if ttc_summary:
        summary_dict = {i['metric']: i['value'] for i in ttc_summary}

        col1, col2, col3 = st.columns(3)

        with col1:
            # Alert Severity Gauge
            critical_pct = (summary_dict.get('Critical', 0) / max(summary_dict.get('Total Alerts', 1), 1)) * 100

            fig_severity = go.Figure(go.Indicator(
                mode="number+gauge",
                value=critical_pct,
                title={'text': "Critical Alert Ratio", 'font': {'size': 20}},
                number={'suffix': '%', 'font': {'size': 36}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkred"},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgreen"},
                        {'range': [25, 50], 'color': "lightyellow"},
                        {'range': [50, 100], 'color': "lightcoral"}
                    ]
                }
            ))
            fig_severity.update_layout(height=250)
            st.plotly_chart(fig_severity, use_container_width=True)

        with col2:
            # Service Type Distribution
            service_data = [
                ('Subway', summary_dict.get('Subway', 0)),
                ('Bus', summary_dict.get('Bus', 0)),
                ('Streetcar', summary_dict.get('Streetcar', 0))
            ]

            fig_services = go.Figure(data=[go.Pie(
                labels=[s[0] for s in service_data],
                values=[s[1] for s in service_data],
                marker=dict(colors=['#0066CC', '#1E90FF', '#4169E1']),
                textinfo='label+value',
                hole=0.3
            )])
            fig_services.update_layout(
                title={'text': 'Alerts by Service', 'x': 0.5, 'xanchor': 'center'},
                height=250
            )
            st.plotly_chart(fig_services, use_container_width=True)

        with col3:
            st.markdown("### Alert Summary")
            st.metric("Total Alerts", summary_dict.get('Total Alerts', 0))
            st.metric("Critical", summary_dict.get('Critical', 0), delta_color="inverse")
            st.metric("High Severity", summary_dict.get('High Severity', 0))

    if ttc_alerts:
        st.subheader("🚨 Active Service Disruptions")
        df_ttc = pd.DataFrame(ttc_alerts).head(15)

        def highlight_severity(row):
            colors = {'High': '#ffcdd2', 'Medium': '#fff9c4', 'Low': '#b3e5fc'}
            color = colors.get(row['Severity'], '#ffffff')
            return [f'background-color: {color}; padding: 10px; border-radius: 5px;'] * len(row)

        styled_df = df_ttc.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #0066CC 0%, #1E90FF 100%); border-radius: 10px; color: white;'>
        <h3>📡 Live Data Feed</h3>
        <p>TTC GTFS-Realtime • Metrolinx Open API • Powered by Streamlit</p>
        <p>Last Updated: {}</p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")), unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if time.time() - st.session_state.last_refresh > 60:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()
