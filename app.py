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

# Ultra-Modern SaaS Dashboard Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        padding: 1.5rem 2.5rem;
        background-color: #f7f8fa;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* Clean metric cards - no individual borders */
    .stMetric {
        background: transparent;
        padding: 0;
        border: none;
        box-shadow: none;
    }
    .stMetric label {
        color: #64748b !important;
        font-weight: 500;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.875rem !important;
        font-weight: 700;
        line-height: 1;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.8125rem !important;
    }

    /* Typography */
    h1 {
        color: #0f172a;
        font-size: 1.875rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    h2 {
        color: #1e293b;
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        letter-spacing: -0.01em;
    }
    h3 {
        color: #475569;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Card container styling */
    .element-container:has(> .stPlotlyChart) {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }

    /* Section subtitle */
    .section-subtitle {
        color: #64748b;
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

    /* Custom divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
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
st.title("Toronto Transit Network")
st.markdown(f"<p class='section-subtitle'>Real-time Operations Monitor • {datetime.now().strftime('%B %d, %Y at %H:%M EST')}</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# NETWORK OVERVIEW - Hero Section
# ============================================================================
st.header("Network Overview")

# Metrics card container
st.markdown("""
    <div style='background: white; border-radius: 16px; padding: 1.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 1.5rem;'>
""", unsafe_allow_html=True)

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
    if ttc_summary and isinstance(ttc_summary, list) and len(ttc_summary) > 0:
        summary_dict = {i['metric']: i['value'] for i in ttc_summary}

        with col4:
            st.metric("🚨 TTC Alerts", summary_dict.get('Total Alerts', 0),
                     delta=f"{summary_dict.get('Critical', 0)} critical",
                     delta_color="inverse" if summary_dict.get('Critical', 0) > 0 else "off")

        with col5:
            total_services = summary_dict.get('Subway', 0) + summary_dict.get('Bus', 0) + summary_dict.get('Streetcar', 0)
            st.metric("🚇 TTC Services", total_services,
                     delta=f"{summary_dict.get('Subway', 0)} subway")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# GO TRANSIT SECTION
# ============================================================================
if show_go:
    st.header("GO Transit Live Status")

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
                title={'text': "On-Time Performance", 'font': {'size': 20, 'color': '#333'}},
                delta={'reference': 95, 'increasing': {'color': '#2e7d32'}, 'decreasing': {'color': '#c62828'}},
                number={'suffix': '%', 'font': {'size': 48}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#666'},
                    'bar': {'color': "#2e7d32", 'thickness': 0.75},
                    'bgcolor': "#f5f5f5",
                    'borderwidth': 1,
                    'bordercolor': "#e0e0e0",
                    'steps': [
                        {'range': [0, 70], 'color': '#ffebee'},
                        {'range': [70, 85], 'color': '#fff3e0'},
                        {'range': [85, 95], 'color': '#e8f5e9'},
                        {'range': [95, 100], 'color': '#c8e6c9'}
                    ],
                    'threshold': {
                        'line': {'color': "#1a1a1a", 'width': 3},
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
                marker=dict(colors=['#00853E', '#757575'], line=dict(color='white', width=2)),
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
                    color=['#2e7d32', '#c62828'],
                    line=dict(color='white', width=2)
                ),
                text=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
                textposition='outside',
                textfont=dict(size=16, color='#333')
            ))

            fig_status.update_layout(
                title={'text': 'Service Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#333'}},
                height=300,
                yaxis_title='Vehicles',
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
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

    # Time Series Trends
    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    if go_timeseries:
        st.subheader("24-Hour Activity Trends")

        fig_ts = go.Figure()
        colors = ['#00853E', '#757575', '#424242']

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
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x|%H:%M}<br>Value: %{y}<extra></extra>'
            ))

        fig_ts.update_layout(
            height=400,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(title=dict(text='Time', font=dict(color='#333')), showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(title=dict(text='Count / Percentage', font=dict(color='#333')), showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=60, r=40, t=40, b=80)
        )

        st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

# ============================================================================
# TTC SECTION
# ============================================================================
if show_ttc:
    st.header("TTC Service Status")

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
                title={'text': "Critical Alert Ratio", 'font': {'size': 20, 'color': '#333'}},
                number={'suffix': '%', 'font': {'size': 36, 'color': '#333'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickcolor': '#666'},
                    'bar': {'color': "#c62828"},
                    'bgcolor': '#f5f5f5',
                    'borderwidth': 1,
                    'bordercolor': '#e0e0e0',
                    'steps': [
                        {'range': [0, 25], 'color': '#e8f5e9'},
                        {'range': [25, 50], 'color': '#fff3e0'},
                        {'range': [50, 100], 'color': '#ffebee'}
                    ]
                }
            ))
            fig_severity.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20))
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
                marker=dict(colors=['#757575', '#9e9e9e', '#bdbdbd'], line=dict(color='white', width=2)),
                textinfo='label+value',
                textfont=dict(size=14),
                hole=0.3
            )])
            fig_services.update_layout(
                title={'text': 'Alerts by Service', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#333'}},
                height=250,
                paper_bgcolor='white',
                plot_bgcolor='white'
            )
            st.plotly_chart(fig_services, use_container_width=True)

        with col3:
            st.markdown("### Alert Summary")
            st.metric("Total Alerts", summary_dict.get('Total Alerts', 0))
            st.metric("Critical", summary_dict.get('Critical', 0), delta_color="inverse")
            st.metric("High Severity", summary_dict.get('High Severity', 0))

    if ttc_alerts and isinstance(ttc_alerts, list) and len(ttc_alerts) > 0:
        st.subheader("Active Service Disruptions")
        df_ttc = pd.DataFrame(ttc_alerts).head(15)

        def highlight_severity(row):
            colors = {'High': '#ffcdd2', 'Medium': '#fff9c4', 'Low': '#b3e5fc'}
            color = colors.get(row['Severity'], '#ffffff')
            return [f'background-color: {color}; padding: 10px; border-radius: 5px;'] * len(row)

        styled_df = df_ttc.style.apply(highlight_severity, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 1.5rem 0; border-top: 1px solid #e2e8f0; margin-top: 2.5rem;'>
        <p style='color: #64748b; font-size: 0.8125rem; margin: 0; font-weight: 500;'>
            TTC GTFS-Realtime • Metrolinx Open API
        </p>
        <p style='color: #94a3b8; font-size: 0.75rem; margin-top: 0.375rem;'>
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
