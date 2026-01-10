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

    /* Bright gradient background */
    .stApp {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
    }

    .main {
        padding: 1.5rem 2rem !important;
        max-width: 1600px;
        margin: 0 auto;
    }

    /* Bright vibrant metric cards */
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
        display: block !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin: 0.25rem 0 !important;
        display: block !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        margin-top: 0.25rem !important;
        color: #64748b !important;
    }

    /* Bright typography */
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

    /* Bright card containers */
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
        color: #64748b;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0.5rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.3px;
    }

    /* Bright divider */
    hr {
        margin: 3rem 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        opacity: 0.4;
    }

    /* Bright sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid #e0e7ff;
        box-shadow: 4px 0 24px rgba(99, 102, 241, 0.1);
    }
    [data-testid="stSidebar"] * {
        color: #1e293b !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: none;
        color: white !important;
        font-weight: 700;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    [data-testid="stSidebar"] .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.5);
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

# Bright Header with Stats Badge
st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <div style='display: inline-block; background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
        border: 2px solid #3b82f6; border-radius: 50px; padding: 0.6rem 1.8rem; margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);'>
            <span style='color: #1e40af; font-weight: 800; font-size: 0.875rem; letter-spacing: 1.5px;'>🚆 LIVE OPERATIONS</span>
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
    # DETAILED SERVICE BREAKDOWN
    # ============================================================================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("📊 Service Breakdown")

    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="small")

    with col1:
        st.metric(
            "🚂 Trains Active",
            stats_dict.get('Trains Active', 0),
            delta=f"{stats_dict.get('Trains in Motion', 0)} moving"
        )

    with col2:
        st.metric(
            "🚌 Buses Active",
            stats_dict.get('Buses Active', 0),
            delta=f"{stats_dict.get('Buses in Motion', 0)} moving"
        )

    with col3:
        st.metric(
            "🛤️ Train Lines",
            stats_dict.get('Train Lines', 0),
            delta="Operational"
        )

    with col4:
        st.metric(
            "🚏 Bus Routes",
            stats_dict.get('Bus Routes', 0),
            delta="Active"
        )

    with col5:
        avg_speed = stats_dict.get('Average Speed', 0)
        st.metric(
            "⚡ Avg Speed",
            f"{avg_speed} km/h",
            delta="Fleet average"
        )

    with col6:
        early = stats_dict.get('Early', 0)
        st.metric(
            "⏰ Early Arrivals",
            early,
            delta=f"{round(early / stats_dict.get('Total Vehicles', 1) * 100)}%"
        )

    # Regional breakdown
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%);
            border: 2px solid #e0e7ff; border-radius: 16px; padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);'>
                <div style='color: #6366f1; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 1rem;'>
                    🌍 REGIONAL COVERAGE
                </div>
                <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem;'>
                    <div style='background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #1e40af; font-size: 0.65rem; font-weight: 700;'>GREATER TORONTO</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Toronto, Mississauga</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #d1fae5 0%, #dbeafe 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #065f46; font-size: 0.65rem; font-weight: 700;'>WESTERN CORRIDOR</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Hamilton, Milton</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #e9d5ff 0%, #fae8ff 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #6b21a8; font-size: 0.65rem; font-weight: 700;'>EASTERN REGION</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Oshawa, Durham</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #92400e; font-size: 0.65rem; font-weight: 700;'>NORTHERN ROUTES</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Barrie, Newmarket</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #991b1b; font-size: 0.65rem; font-weight: 700;'>WESTERN ONTARIO</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Kitchener, Guelph</div>
                    </div>
                    <div style='background: linear-gradient(135deg, #bfdbfe 0%, #dbeafe 100%); padding: 0.75rem; border-radius: 10px;'>
                        <div style='color: #1e40af; font-size: 0.65rem; font-weight: 700;'>NIAGARA REGION</div>
                        <div style='color: #0f172a; font-size: 1.25rem; font-weight: 900;'>Niagara Falls</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #fef3c7 0%, #fef9c3 100%);
            border: 2px solid #fbbf24; border-radius: 16px; padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(251, 191, 36, 0.15); height: 100%;'>
                <div style='color: #92400e; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 1rem;'>
                    ⚡ LIVE STATS
                </div>
                <div style='margin-bottom: 1rem;'>
                    <div style='color: #78350f; font-size: 0.65rem; font-weight: 700; margin-bottom: 0.25rem;'>FLEET IN MOTION</div>
                    <div style='color: #0f172a; font-size: 1.75rem; font-weight: 900;'>
                        {stats_dict.get('Trains in Motion', 0) + stats_dict.get('Buses in Motion', 0)}
                        <span style='font-size: 0.875rem; color: #78350f;'>/{stats_dict.get('Total Vehicles', 0)}</span>
                    </div>
                </div>
                <div style='margin-bottom: 1rem;'>
                    <div style='color: #78350f; font-size: 0.65rem; font-weight: 700; margin-bottom: 0.25rem;'>SERVICE RELIABILITY</div>
                    <div style='color: #0f172a; font-size: 1.75rem; font-weight: 900;'>
                        {stats_dict.get('Performance Rate', 0)}%
                    </div>
                </div>
                <div>
                    <div style='color: #78350f; font-size: 0.65rem; font-weight: 700; margin-bottom: 0.25rem;'>PEAK CAPACITY</div>
                    <div style='color: #0f172a; font-size: 1.75rem; font-weight: 900;'>Active</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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
            title={'text': "On-Time Performance", 'font': {'size': 18, 'color': '#1e293b', 'family': 'Plus Jakarta Sans', 'weight': 700}},
            delta={'reference': 95, 'increasing': {'color': '#10b981'}, 'decreasing': {'color': '#ef4444'}},
            number={'suffix': '%', 'font': {'size': 40, 'color': '#0f172a', 'family': 'Plus Jakarta Sans', 'weight': 800}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': '#64748b', 'tickfont': {'color': '#475569', 'size': 11}},
                'bar': {'color': "#3b82f6", 'thickness': 0.75},
                'bgcolor': "#f1f5f9",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 70], 'color': '#fee2e2'},
                    {'range': [70, 85], 'color': '#fef3c7'},
                    {'range': [85, 95], 'color': '#dbeafe'},
                    {'range': [95, 100], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': "#8b5cf6", 'width': 3},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        fig_gauge.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=80, b=10),
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans')
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
            textfont=dict(size=15, color='#1e293b', family='Plus Jakarta Sans', weight=600),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig_fleet.update_layout(
            title={'text': 'Fleet Distribution', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#1e293b', 'family': 'Plus Jakarta Sans'}},
            height=320,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='#334155', size=12, family='Plus Jakarta Sans')
            ),
            paper_bgcolor='#ffffff',
            plot_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans')
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
            textfont=dict(size=18, color='#0f172a', family='Plus Jakarta Sans', weight=700)
        ))

        fig_status.update_layout(
            title={'text': 'Service Status', 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': '#1e293b', 'family': 'Plus Jakarta Sans'}},
            height=320,
            yaxis=dict(
                title='Vehicles',
                color='#64748b',
                gridcolor='#e2e8f0',
                tickfont=dict(color='#334155', family='Plus Jakarta Sans')
            ),
            xaxis=dict(
                color='#334155',
                tickfont=dict(color='#334155', size=13, family='Plus Jakarta Sans', weight=600)
            ),
            showlegend=False,
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#1e293b', family='Plus Jakarta Sans'),
            margin=dict(l=50, r=30, t=80, b=50)
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col4:
        # Key Metrics - Bright Cards
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
            border: 2px solid #93c5fd; border-radius: 14px; padding: 1.2rem; margin-bottom: 0.8rem;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);'>
                <div style='color: #1e40af; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Total Fleet</div>
                <div style='color: #0f172a; font-size: 1.9rem; font-weight: 900; line-height: 1.2;'>{stats_dict.get('Total Vehicles', 0)}</div>
                <div style='color: #2563eb; font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem;'>● Active Now</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #d1fae5 0%, #dbeafe 100%);
            border: 2px solid #6ee7b7; border-radius: 14px; padding: 1.2rem; margin-bottom: 0.8rem;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);'>
                <div style='color: #065f46; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Train Lines</div>
                <div style='color: #0f172a; font-size: 1.9rem; font-weight: 900; line-height: 1.2;'>{stats_dict.get('Train Lines', 0)}</div>
                <div style='color: #059669; font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem;'>● Operational</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e9d5ff 0%, #fae8ff 100%);
            border: 2px solid #d8b4fe; border-radius: 14px; padding: 1.2rem;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);'>
                <div style='color: #6b21a8; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Bus Routes</div>
                <div style='color: #0f172a; font-size: 1.9rem; font-weight: 900; line-height: 1.2;'>{stats_dict.get('Bus Routes', 0)}</div>
                <div style='color: #7c3aed; font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem;'>● In Service</div>
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
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            xaxis=dict(
                title=dict(text='Time', font=dict(color='#1e293b', size=14, family='Plus Jakarta Sans')),
                showgrid=True,
                gridcolor='#e2e8f0',
                color='#334155',
                tickfont=dict(color='#64748b', family='Plus Jakarta Sans')
            ),
            yaxis=dict(
                title=dict(text='Count / Percentage', font=dict(color='#1e293b', size=14, family='Plus Jakarta Sans')),
                showgrid=True,
                gridcolor='#e2e8f0',
                color='#334155',
                tickfont=dict(color='#64748b', family='Plus Jakarta Sans')
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.12,
                xanchor="center",
                x=0.5,
                font=dict(color='#334155', size=13, family='Plus Jakarta Sans'),
                bgcolor='#f8fafc',
                bordercolor='#e0e7ff',
                borderwidth=2
            ),
            font=dict(color='#1e293b', family='Plus Jakarta Sans'),
            margin=dict(l=70, r=40, t=50, b=90)
        )

        st.plotly_chart(fig_ts, use_container_width=True)

# ============================================================================
# INTERACTIVE ROUTE TRACKING
# ============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.header("🗺️ Live Route Tracking")
st.markdown("<p class='section-subtitle'>Select a route to view live vehicle positions on the map</p>", unsafe_allow_html=True)

# Fetch vehicle data
from route_data import GO_ROUTES, get_route_name
go_vehicles = fetch_data(f"{GO_API}?type=vehicles")

if go_vehicles:
    df_vehicles = pd.DataFrame(go_vehicles)

    # Get available routes with active vehicles
    if 'RouteCode' in df_vehicles.columns:
        active_routes = df_vehicles['RouteCode'].unique()
        train_routes = [r for r in active_routes if r in ['ST', 'RH', 'MI', 'LW', 'LE', 'KI', 'BR', 'GT']]
        bus_routes = [r for r in active_routes if r not in train_routes]

        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
                border: 2px solid #3b82f6; border-radius: 16px; padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);'>
                    <div style='color: #1e40af; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 1rem;'>
                        📍 SELECT ROUTE
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Train routes section
            if train_routes:
                st.markdown("**🚂 Train Lines**")
                selected_route = st.selectbox(
                    "Train routes:",
                    options=[''] + sorted(train_routes),
                    format_func=lambda x: f"{get_route_name(x)} ({x})" if x else "Choose a train line...",
                    label_visibility="collapsed"
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Bus routes section
            if bus_routes and not selected_route:
                st.markdown("**🚌 Bus Routes**")
                selected_route = st.selectbox(
                    "Bus routes:",
                    options=[''] + sorted(bus_routes, key=lambda x: int(x) if x.isdigit() else 999),
                    format_func=lambda x: f"{get_route_name(x)} ({x})" if x else "Choose a bus route...",
                    label_visibility="collapsed"
                )

        with col2:
            if selected_route:
                # Filter vehicles for selected route
                route_vehicles = df_vehicles[df_vehicles['RouteCode'] == selected_route]
                route_vehicles_with_loc = route_vehicles[(route_vehicles['Latitude'] != 0) & (route_vehicles['Longitude'] != 0)]

                if not route_vehicles_with_loc.empty:
                    # Display route info
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #ffffff 0%, #fefefe 100%);
                        border: 2px solid #e0e7ff; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
                        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);'>
                            <div style='color: #6366f1; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 0.5rem;'>
                                NOW TRACKING
                            </div>
                            <div style='color: #0f172a; font-size: 1.5rem; font-weight: 900; margin-bottom: 0.5rem;'>
                                {get_route_name(selected_route)}
                            </div>
                            <div style='color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                                🚦 {len(route_vehicles_with_loc)} vehicles active • Route {selected_route}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Create map
                    center_lat = route_vehicles_with_loc['Latitude'].mean()
                    center_lon = route_vehicles_with_loc['Longitude'].mean()

                    # Determine zoom
                    lat_range = route_vehicles_with_loc['Latitude'].max() - route_vehicles_with_loc['Latitude'].min()
                    lon_range = route_vehicles_with_loc['Longitude'].max() - route_vehicles_with_loc['Longitude'].min()
                    max_range = max(lat_range, lon_range)

                    if max_range < 0.1:
                        zoom = 12
                    elif max_range < 0.5:
                        zoom = 10
                    elif max_range < 1.0:
                        zoom = 9
                    else:
                        zoom = 8

                    import plotly.express as px

                    fig_route_map = px.scatter_mapbox(
                        route_vehicles_with_loc,
                        lat="Latitude",
                        lon="Longitude",
                        color="Status",
                        size=[15] * len(route_vehicles_with_loc),
                        hover_name="Display",
                        hover_data={
                            "TripNumber": True,
                            "Status": True,
                            "IsInMotion": True,
                            "Latitude": ":.4f",
                            "Longitude": ":.4f"
                        },
                        color_discrete_map={"On Time": "#10b981", "Delayed": "#ef4444", "Early": "#3b82f6"},
                        zoom=zoom,
                        height=500,
                        center={"lat": center_lat, "lon": center_lon}
                    )

                    fig_route_map.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r": 0, "t": 0, "l": 0, "b": 0},
                        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_color="#0f172a"),
                        paper_bgcolor='#ffffff',
                        plot_bgcolor='#ffffff'
                    )

                    st.plotly_chart(fig_route_map, use_container_width=True)

                    # Vehicle details
                    st.markdown("**🚦 Active Vehicles**")
                    vehicle_details = route_vehicles[['Display', 'Status', 'TripNumber', 'IsInMotion']].copy()
                    vehicle_details['IsInMotion'] = vehicle_details['IsInMotion'].map({True: '🟢 Moving', False: '🔴 Stopped'})
                    st.dataframe(vehicle_details, use_container_width=True, height=200)
                else:
                    st.info(f"No vehicles with GPS data found for {get_route_name(selected_route)} at this time.")
            else:
                # Show instruction card
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #f0f9ff 0%, #e0e7ff 100%);
                    border: 2px dashed #3b82f6; border-radius: 16px; padding: 3rem; text-align: center;
                    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.1);'>
                        <div style='font-size: 3rem; margin-bottom: 1rem;'>🗺️</div>
                        <div style='color: #1e293b; font-size: 1.25rem; font-weight: 700; margin-bottom: 0.75rem;'>
                            Select a Route to Begin Tracking
                        </div>
                        <div style='color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                            Choose a train line or bus route from the left sidebar to view live vehicle positions
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Unable to load route data at this time.")
else:
    st.warning("Unable to load vehicle data for route tracking.")

# Bright Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2.5rem 0; margin-top: 3rem;
    background: linear-gradient(135deg, #dbeafe 0%, #e0e7ff 100%);
    border-top: 3px solid #3b82f6;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.15);'>
        <div style='color: #1e40af; font-size: 0.875rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 0.75rem;'>
            ⚡ POWERED BY
        </div>
        <div style='background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 1.25rem; font-weight: 900; margin-bottom: 1rem;'>
            Metrolinx Open API
        </div>
        <div style='color: #475569; font-size: 0.875rem; font-weight: 600;'>
            🔄 Live Updates Every 60s • Last Refresh: {} EST
        </div>
        <div style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid rgba(59, 130, 246, 0.2);'>
            <div style='color: #64748b; font-size: 0.75rem; font-weight: 600;'>
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
