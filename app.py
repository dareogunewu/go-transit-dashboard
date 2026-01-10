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

# Modern Premium Dashboard Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Premium gradient background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1629 100%);
    }

    .main {
        padding: 1.5rem 2rem !important;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* Glass-morphism metric cards */
    .stMetric {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 16px !important;
        padding: 1.25rem 1rem !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 120px;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
    }
    .stMetric label {
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem !important;
        display: block !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
        margin: 0.25rem 0 !important;
        display: block !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        margin-top: 0.25rem !important;
    }

    /* Premium typography */
    h1 {
        color: #f8fafc;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 80px rgba(59, 130, 246, 0.5);
    }
    h2 {
        color: #e2e8f0;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 3rem 0 1.5rem 0;
        position: relative;
        padding-bottom: 1rem;
    }
    h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 2px;
    }
    h3 {
        color: #cbd5e1;
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Premium card containers */
    .element-container:has(> .stPlotlyChart) {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    .element-container:has(> .stPlotlyChart):hover {
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.25);
    }

    /* Fix column gaps */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }

    [data-testid="column"]:first-child {
        padding-left: 0;
    }

    [data-testid="column"]:last-child {
        padding-right: 0;
    }

    /* Accent colors */
    .accent-blue { color: #3b82f6; }
    .accent-purple { color: #8b5cf6; }
    .accent-pink { color: #ec4899; }
    .accent-green { color: #10b981; }
    .accent-orange { color: #f59e0b; }

    /* Section subtitle */
    .section-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 500;
        margin-top: 0.5rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.3px;
    }

    /* Glowing divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        opacity: 0.3;
    }

    /* Premium sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
        box-shadow: 4px 0 24px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: none;
        color: white;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }

    /* Code/monospace font for metrics */
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .main > div {
        animation: fadeInUp 0.6s ease-out;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
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

# Premium Header with Stats Badge
st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <div style='display: inline-block; background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 50px; padding: 0.5rem 1.5rem; margin-bottom: 1rem;'>
            <span style='color: #3b82f6; font-weight: 600; font-size: 0.875rem; letter-spacing: 1px;'>🚆 LIVE OPERATIONS</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.title("GO Transit Command Center")
st.markdown(f"<p class='section-subtitle'>Real-time Performance Analytics • {datetime.now().strftime('%B %d, %Y at %H:%M EST')}</p>", unsafe_allow_html=True)

# ============================================================================
# NETWORK OVERVIEW - Hero Section
# ============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.header("Network Overview")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="medium")

go_stats = fetch_data(f"{GO_API}?type=stats")
if go_stats and isinstance(go_stats, list) and len(go_stats) > 0:
    stats_dict = {i['metric']: i['value'] for i in go_stats}
else:
    st.warning("⚠️ Unable to load GO Transit statistics")
    stats_dict = {}

if stats_dict:
    with col1:
        st.metric(
            "System Performance",
            f"{stats_dict.get('Performance Rate', 0)}%",
            delta=f"{stats_dict.get('Performance Rate', 0) - 95}% vs target",
            delta_color="normal" if stats_dict.get('Performance Rate', 0) >= 95 else "inverse"
        )

    with col2:
        st.metric(
            "Active Fleet",
            stats_dict.get('Total Vehicles', 0),
            delta=f"{stats_dict.get('Trains in Motion', 0) + stats_dict.get('Buses in Motion', 0)} in motion"
        )

    with col3:
        st.metric(
            "On-Time Vehicles",
            stats_dict.get('On Time', 0),
            delta=f"{round(stats_dict.get('On Time', 0) / stats_dict.get('Total Vehicles', 1) * 100)}%"
        )

    with col4:
        delayed_pct = round((stats_dict.get('Delayed', 0) / stats_dict.get('Total Vehicles', 1) * 100))
        st.metric(
            "Delayed Vehicles",
            stats_dict.get('Delayed', 0),
            delta=f"{delayed_pct}%",
            delta_color="inverse"
        )

# ============================================================================
# GO TRANSIT SECTION
# ============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.header("GO Transit Live Status")
st.markdown("<br>", unsafe_allow_html=True)

go_stats = fetch_data(f"{GO_API}?type=stats")
if go_stats:
    stats_dict = {i['metric']: i['value'] for i in go_stats}

    # Performance Dashboard
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="medium")

    with col1:
        # Performance Gauge - Premium Theme
        perf_value = stats_dict.get('Performance Rate', 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=perf_value,
            title={'text': "On-Time Performance", 'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Plus Jakarta Sans'}},
            delta={'reference': 95, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#f59e0b'}},
            number={'suffix': '%', 'font': {'size': 48, 'color': '#f8fafc', 'family': 'Plus Jakarta Sans'}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#64748b', 'tickfont': {'color': '#94a3b8'}},
                'bar': {'color': "#3b82f6", 'thickness': 0.8},
                'bgcolor': "rgba(15, 23, 42, 0.5)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 70], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [70, 85], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [85, 95], 'color': 'rgba(59, 130, 246, 0.2)'},
                    {'range': [95, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': "#8b5cf6", 'width': 4},
                    'thickness': 0.8,
                    'value': 95
                }
            }
        ))
        fig_gauge.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=80, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0', family='Plus Jakarta Sans')
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Service Distribution - Premium Theme
        fig_fleet = go.Figure(data=[go.Pie(
            labels=['Trains', 'Buses'],
            values=[stats_dict.get('Trains Active', 0), stats_dict.get('Buses Active', 0)],
            hole=0.5,
            marker=dict(
                colors=['#3b82f6', '#8b5cf6'],
                line=dict(color='rgba(255,255,255,0.1)', width=3)
            ),
            textinfo='label+value+percent',
            textfont=dict(size=15, color='#f8fafc', family='Plus Jakarta Sans', weight=600),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig_fleet.update_layout(
            title={'text': 'Fleet Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Plus Jakarta Sans'}},
            height=320,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='#cbd5e1', size=12, family='Plus Jakarta Sans')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0', family='Plus Jakarta Sans')
        )
        st.plotly_chart(fig_fleet, use_container_width=True)

    with col3:
        # On-Time vs Delayed - Premium Theme
        fig_status = go.Figure()

        fig_status.add_trace(go.Bar(
            x=['On Time', 'Delayed'],
            y=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
            marker=dict(
                color=['#10b981', '#ec4899'],
                line=dict(color='rgba(255,255,255,0.1)', width=2),
                pattern=dict(shape=['', '/'], solidity=0.3)
            ),
            text=[stats_dict.get('On Time', 0), stats_dict.get('Delayed', 0)],
            textposition='outside',
            textfont=dict(size=18, color='#f8fafc', family='Plus Jakarta Sans', weight=700)
        ))

        fig_status.update_layout(
            title={'text': 'Service Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#e2e8f0', 'family': 'Plus Jakarta Sans'}},
            height=320,
            yaxis=dict(
                title='Vehicles',
                color='#94a3b8',
                gridcolor='rgba(148, 163, 184, 0.1)',
                tickfont=dict(color='#cbd5e1', family='Plus Jakarta Sans')
            ),
            xaxis=dict(
                color='#cbd5e1',
                tickfont=dict(color='#cbd5e1', size=13, family='Plus Jakarta Sans', weight=600)
            ),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0', family='Plus Jakarta Sans'),
            margin=dict(l=50, r=30, t=80, b=50)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col4:
        # Key Metrics - Premium Cards (Fixed spacing)
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;'>
                <div style='color: #94a3b8; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem;'>Total Fleet</div>
                <div style='color: #f8fafc; font-size: 1.75rem; font-weight: 700; line-height: 1.2;'>{stats_dict.get('Total Vehicles', 0)}</div>
                <div style='color: #3b82f6; font-size: 0.75rem; font-weight: 500; margin-top: 0.4rem;'>● Active Now</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;'>
                <div style='color: #94a3b8; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem;'>Train Lines</div>
                <div style='color: #f8fafc; font-size: 1.75rem; font-weight: 700; line-height: 1.2;'>{stats_dict.get('Train Lines', 0)}</div>
                <div style='color: #10b981; font-size: 0.75rem; font-weight: 500; margin-top: 0.4rem;'>● Operational</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%);
            border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 12px; padding: 1rem;'>
                <div style='color: #94a3b8; font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem;'>Bus Routes</div>
                <div style='color: #f8fafc; font-size: 1.75rem; font-weight: 700; line-height: 1.2;'>{stats_dict.get('Bus Routes', 0)}</div>
                <div style='color: #8b5cf6; font-size: 0.75rem; font-weight: 500; margin-top: 0.4rem;'>● In Service</div>
            </div>
        """, unsafe_allow_html=True)

    # Time Series Trends - Premium Theme
    st.markdown("<br><br>", unsafe_allow_html=True)
    go_timeseries = fetch_data(f"{GO_API}?type=timeseries")
    if go_timeseries:
        st.subheader("24-Hour Activity Trends")
        st.markdown("<br>", unsafe_allow_html=True)

        fig_ts = go.Figure()
        colors = ['#3b82f6', '#8b5cf6', '#10b981']
        fills = ['rgba(59, 130, 246, 0.1)', 'rgba(139, 92, 246, 0.1)', 'rgba(16, 185, 129, 0.1)']

        for idx, series in enumerate(go_timeseries):
            timestamps = [datetime.fromtimestamp(p[1]/1000) for p in series['datapoints']]
            values = [p[0] for p in series['datapoints']]

            fig_ts.add_trace(go.Scatter(
                x=timestamps,
                y=values,
                mode='lines+markers',
                name=series['target'],
                line=dict(width=3, color=colors[idx % len(colors)], shape='spline'),
                marker=dict(size=7, color=colors[idx % len(colors)], line=dict(color='#f8fafc', width=2)),
                fill='tozeroy',
                fillcolor=fills[idx % len(fills)],
                hovertemplate='<b>%{fullData.name}</b><br>Time: %{x|%H:%M}<br>Value: %{y}<extra></extra>'
            ))

        fig_ts.update_layout(
            height=450,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                title=dict(text='Time', font=dict(color='#e2e8f0', size=14, family='Plus Jakarta Sans')),
                showgrid=True,
                gridcolor='rgba(148, 163, 184, 0.1)',
                color='#cbd5e1',
                tickfont=dict(color='#94a3b8', family='Plus Jakarta Sans')
            ),
            yaxis=dict(
                title=dict(text='Count / Percentage', font=dict(color='#e2e8f0', size=14, family='Plus Jakarta Sans')),
                showgrid=True,
                gridcolor='rgba(148, 163, 184, 0.1)',
                color='#cbd5e1',
                tickfont=dict(color='#94a3b8', family='Plus Jakarta Sans')
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.12,
                xanchor="center",
                x=0.5,
                font=dict(color='#cbd5e1', size=13, family='Plus Jakarta Sans'),
                bgcolor='rgba(255,255,255,0.05)',
                bordercolor='rgba(255,255,255,0.1)',
                borderwidth=1
            ),
            font=dict(color='#e2e8f0', family='Plus Jakarta Sans'),
            margin=dict(l=70, r=40, t=50, b=90)
        )

        st.plotly_chart(fig_ts, use_container_width=True)


# Premium Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2.5rem 0; margin-top: 3rem;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border-top: 2px solid rgba(59, 130, 246, 0.2);
    border-radius: 20px 20px 0 0;'>
        <div style='color: #94a3b8; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.75rem;'>
            ⚡ POWERED BY
        </div>
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 1.125rem; font-weight: 700; margin-bottom: 1rem;'>
            Metrolinx Open API
        </div>
        <div style='color: #64748b; font-size: 0.8125rem; font-weight: 500;'>
            🔄 Live Updates Every 60s • Last Refresh: {} EST
        </div>
        <div style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(148, 163, 184, 0.15);'>
            <div style='color: #475569; font-size: 0.75rem;'>
                Built with Streamlit • Real-time Transit Intelligence
            </div>
        </div>
    </div>
""".format(datetime.now().strftime("%H:%M")), unsafe_allow_html=True)

# Auto-refresh
if auto_refresh:
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if time.time() - st.session_state.last_refresh > 60:
        st.session_state.last_refresh = time.time()
        st.cache_data.clear()
        st.rerun()
