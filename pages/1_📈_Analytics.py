"""
GO Transit Analytics - Daily, Weekly & Monthly Stats
Comprehensive performance analytics and trends
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from route_data import get_route_name

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

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

    .metric-card {
        background: #242629;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #2e3034;
        box-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }

    .status-good {color: #73bf69; font-weight: 500;}
    .status-warning {color: #f5a742; font-weight: 500;}
    .status-critical {color: #ff5705; font-weight: 500;}

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

# Generate simulated historical data (in production, this would come from a database)
@st.cache_data(ttl=3600)
def generate_historical_data(days=30):
    """Generate simulated historical performance data"""
    dates = [datetime.now() - timedelta(days=x) for x in range(days)]
    dates.reverse()

    data = []
    for date in dates:
        # Simulate realistic patterns
        is_weekend = date.weekday() >= 5
        is_peak = 7 <= date.hour <= 9 or 16 <= date.hour <= 19

        base_performance = 85 if is_weekend else 80
        peak_penalty = -5 if is_peak else 0
        random_variation = np.random.randint(-3, 8)

        performance = min(100, max(65, base_performance + peak_penalty + random_variation))

        trains = np.random.randint(18, 28)
        buses = np.random.randint(140, 180)

        data.append({
            'date': date,
            'performance': performance,
            'trains': trains,
            'buses': buses,
            'total_vehicles': trains + buses,
            'delayed': int((100 - performance) / 100 * (trains + buses)),
            'on_time': int(performance / 100 * (trains + buses))
        })

    return pd.DataFrame(data)

# Header
st.title("GO Transit Analytics")
st.markdown(f"<p class='section-subtitle'>Comprehensive Performance Analysis • {datetime.now().strftime('%B %d, %Y at %H:%M EST')}</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Analytics Controls")

    time_range = st.selectbox(
        "Time Range",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )

    days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90}
    days = days_map[time_range]

    st.markdown("---")
    st.markdown("### 📁 Report Sections")
    show_overview = st.checkbox("Performance Overview", value=True)
    show_trends = st.checkbox("Trend Analysis", value=True)
    show_routes = st.checkbox("Route Performance", value=True)
    show_insights = st.checkbox("Key Insights", value=True)

# Fetch current data
go_stats = fetch_data(f"{GO_API}?type=stats")
go_lines_trains = fetch_data(f"{GO_API}?type=lines&vehicleType=trains")
go_lines_buses = fetch_data(f"{GO_API}?type=lines&vehicleType=buses")

# Generate historical data
df_history = generate_historical_data(days)

# ============================================================================
# PERFORMANCE OVERVIEW
# ============================================================================
if show_overview:
    st.header("📊 Performance Overview")

    # Calculate metrics
    avg_performance = df_history['performance'].mean()
    current_performance = df_history['performance'].iloc[-1]
    performance_trend = current_performance - df_history['performance'].iloc[0]

    avg_vehicles = df_history['total_vehicles'].mean()
    avg_delays = df_history['delayed'].mean()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Avg Performance",
            f"{avg_performance:.1f}%",
            delta=f"{performance_trend:+.1f}% vs start",
            delta_color="normal"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Current Performance",
            f"{current_performance:.0f}%",
            delta=f"{current_performance - avg_performance:+.1f}% vs avg"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Avg Daily Vehicles",
            f"{avg_vehicles:.0f}",
            delta=f"{df_history['total_vehicles'].iloc[-1] - avg_vehicles:+.0f} today"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Avg Daily Delays",
            f"{avg_delays:.0f}",
            delta=f"{df_history['delayed'].iloc[-1] - avg_delays:+.0f} today",
            delta_color="inverse"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        best_day = df_history.loc[df_history['performance'].idxmax()]
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Best Performance",
            f"{best_day['performance']:.0f}%",
            delta=best_day['date'].strftime("%b %d")
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

# ============================================================================
# TREND ANALYSIS
# ============================================================================
if show_trends:
    st.header("📈 Trend Analysis")

    tab1, tab2, tab3 = st.tabs(["📅 Daily", "📊 Weekly", "📆 Monthly"])

    with tab1:
        st.subheader("Daily Performance Trends")

        # Performance over time - Dark Theme
        fig_daily = go.Figure()

        fig_daily.add_trace(go.Scatter(
            x=df_history['date'],
            y=df_history['performance'],
            mode='lines+markers',
            name='Performance %',
            line=dict(color='#73bf69', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(115, 191, 105, 0.1)',
            hovertemplate='<b>Date:</b> %{x|%b %d}<br><b>Performance:</b> %{y:.1f}%<extra></extra>'
        ))

        # Add target line
        fig_daily.add_hline(
            y=95,
            line_dash="dash",
            line_color="#ff5705",
            annotation_text="Target: 95%",
            annotation_position="right",
            annotation_font=dict(color='#d8d9da')
        )

        # Add moving average
        df_history['ma_7'] = df_history['performance'].rolling(window=min(7, len(df_history))).mean()
        fig_daily.add_trace(go.Scatter(
            x=df_history['date'],
            y=df_history['ma_7'],
            mode='lines',
            name='7-Day Moving Avg',
            line=dict(color='#9fa3a8', width=2, dash='dot'),
            hovertemplate='<b>7-Day Avg:</b> %{y:.1f}%<extra></extra>'
        ))

        fig_daily.update_layout(
            height=450,
            hovermode='x unified',
            plot_bgcolor='#242629',
            paper_bgcolor='#242629',
            font=dict(color='#d8d9da'),
            xaxis=dict(
                title=dict(text='Date', font=dict(color='#d8d9da')),
                showgrid=True,
                gridcolor='#2e3034',
                color='#d8d9da'
            ),
            yaxis=dict(
                title=dict(text='Performance %', font=dict(color='#d8d9da')),
                range=[60, 105],
                showgrid=True,
                gridcolor='#2e3034',
                color='#d8d9da'
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(color='#d8d9da')
            )
        )

        st.plotly_chart(fig_daily, use_container_width=True)

        # Vehicle activity
        col1, col2 = st.columns(2)

        with col1:
            fig_vehicles = go.Figure()

            fig_vehicles.add_trace(go.Bar(
                x=df_history['date'],
                y=df_history['trains'],
                name='Trains',
                marker=dict(color='#73bf69'),
                hovertemplate='Trains: %{y}<extra></extra>'
            ))

            fig_vehicles.add_trace(go.Bar(
                x=df_history['date'],
                y=df_history['buses'],
                name='Buses',
                marker=dict(color='#6e9bd1'),
                hovertemplate='Buses: %{y}<extra></extra>'
            ))

            fig_vehicles.update_layout(
                title={'text': 'Daily Vehicle Count', 'font': {'color': '#d8d9da'}},
                barmode='stack',
                height=350,
                hovermode='x unified',
                plot_bgcolor='#242629',
                paper_bgcolor='#242629',
                font=dict(color='#d8d9da'),
                xaxis=dict(title=dict(text='Date', font=dict(color='#d8d9da')), color='#d8d9da', gridcolor='#2e3034'),
                yaxis=dict(title=dict(text='Vehicles', font=dict(color='#d8d9da')), color='#d8d9da', gridcolor='#2e3034'),
                legend=dict(font=dict(color='#d8d9da'))
            )

            st.plotly_chart(fig_vehicles, use_container_width=True)

        with col2:
            fig_delays = go.Figure()

            fig_delays.add_trace(go.Scatter(
                x=df_history['date'],
                y=df_history['on_time'],
                mode='lines',
                name='On Time',
                fill='tonexty',
                line=dict(color='#73bf69', width=2),
                stackgroup='one'
            ))

            fig_delays.add_trace(go.Scatter(
                x=df_history['date'],
                y=df_history['delayed'],
                mode='lines',
                name='Delayed',
                fill='tonexty',
                line=dict(color='#ff5705', width=2),
                stackgroup='one'
            ))

            fig_delays.update_layout(
                title={'text': 'On-Time vs Delayed Vehicles', 'font': {'color': '#d8d9da'}},
                height=350,
                hovermode='x unified',
                plot_bgcolor='#242629',
                paper_bgcolor='#242629',
                font=dict(color='#d8d9da'),
                xaxis=dict(title=dict(text='Date', font=dict(color='#d8d9da')), color='#d8d9da', gridcolor='#2e3034'),
                yaxis=dict(title=dict(text='Vehicles', font=dict(color='#d8d9da')), color='#d8d9da', gridcolor='#2e3034'),
                legend=dict(font=dict(color='#d8d9da'))
            )

            st.plotly_chart(fig_delays, use_container_width=True)

    with tab2:
        st.subheader("Weekly Performance Analysis")

        # Group by week
        df_history['week'] = df_history['date'].dt.to_period('W').dt.to_timestamp()
        df_weekly = df_history.groupby('week').agg({
            'performance': 'mean',
            'total_vehicles': 'mean',
            'delayed': 'mean',
            'on_time': 'mean'
        }).reset_index()

        col1, col2 = st.columns(2)

        with col1:
            fig_weekly_perf = go.Figure()

            fig_weekly_perf.add_trace(go.Bar(
                x=df_weekly['week'],
                y=df_weekly['performance'],
                marker=dict(
                    color=df_weekly['performance'],
                    colorscale='RdYlGn',
                    cmin=70,
                    cmax=100,
                    colorbar=dict(title="Performance %")
                ),
                text=[f"{p:.1f}%" for p in df_weekly['performance']],
                textposition='outside',
                hovertemplate='<b>Week of %{x|%b %d}</b><br>Avg Performance: %{y:.1f}%<extra></extra>'
            ))

            fig_weekly_perf.update_layout(
                title='Weekly Average Performance',
                height=400,
                xaxis_title='Week',
                yaxis_title='Performance %',
                yaxis_range=[60, 105]
            )

            st.plotly_chart(fig_weekly_perf, use_container_width=True)

        with col2:
            fig_weekly_vehicles = go.Figure()

            fig_weekly_vehicles.add_trace(go.Scatter(
                x=df_weekly['week'],
                y=df_weekly['total_vehicles'],
                mode='lines+markers',
                name='Avg Vehicles',
                line=dict(color='#0066CC', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(0, 102, 204, 0.2)'
            ))

            fig_weekly_vehicles.update_layout(
                title='Weekly Average Vehicles',
                height=400,
                xaxis_title='Week',
                yaxis_title='Vehicles'
            )

            st.plotly_chart(fig_weekly_vehicles, use_container_width=True)

    with tab3:
        st.subheader("Monthly Performance Summary")

        # Group by month
        df_history['month'] = df_history['date'].dt.to_period('M').dt.to_timestamp()
        df_monthly = df_history.groupby('month').agg({
            'performance': ['mean', 'min', 'max', 'std'],
            'total_vehicles': ['mean', 'sum'],
            'delayed': ['mean', 'sum']
        }).reset_index()

        df_monthly.columns = ['_'.join(col).strip('_') for col in df_monthly.columns.values]

        # Monthly summary table
        st.markdown("### Monthly Statistics")

        summary_df = pd.DataFrame({
            'Month': df_monthly['month'].dt.strftime('%B %Y'),
            'Avg Performance': df_monthly['performance_mean'].round(1).astype(str) + '%',
            'Best Day': df_monthly['performance_max'].round(1).astype(str) + '%',
            'Worst Day': df_monthly['performance_min'].round(1).astype(str) + '%',
            'Volatility (σ)': df_monthly['performance_std'].round(2),
            'Total Vehicles': df_monthly['total_vehicles_sum'].astype(int),
            'Total Delays': df_monthly['delayed_sum'].astype(int)
        })

        st.dataframe(summary_df, use_container_width=True, height=200)

        # Monthly visualizations
        col1, col2 = st.columns(2)

        with col1:
            fig_monthly_box = go.Figure()

            for i, month in enumerate(df_monthly['month']):
                month_data = df_history[df_history['month'] == month]

                fig_monthly_box.add_trace(go.Box(
                    y=month_data['performance'],
                    name=month.strftime('%b'),
                    marker_color=['#00853E', '#0066CC', '#FF6B35'][i % 3],
                    boxmean='sd'
                ))

            fig_monthly_box.update_layout(
                title='Monthly Performance Distribution',
                height=400,
                yaxis_title='Performance %',
                showlegend=False
            )

            st.plotly_chart(fig_monthly_box, use_container_width=True)

        with col2:
            fig_monthly_heatmap = go.Figure(data=go.Heatmap(
                x=df_history['date'].dt.day,
                y=df_history['date'].dt.strftime('%B'),
                z=df_history['performance'],
                colorscale='RdYlGn',
                zmin=70,
                zmax=100,
                colorbar=dict(title="Performance %"),
                hovertemplate='Day: %{x}<br>Month: %{y}<br>Performance: %{z:.1f}%<extra></extra>'
            ))

            fig_monthly_heatmap.update_layout(
                title='Performance Heatmap',
                height=400,
                xaxis_title='Day of Month',
                yaxis_title='Month'
            )

            st.plotly_chart(fig_monthly_heatmap, use_container_width=True)

    st.markdown("---")

# ============================================================================
# ROUTE PERFORMANCE
# ============================================================================
if show_routes:
    st.header("🚂 Route Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Train Lines")
        if go_lines_trains:
            df_trains = pd.DataFrame(go_lines_trains)
            df_trains['LineName'] = df_trains['Code'].apply(get_route_name)
            df_trains['OnTimeRate'] = (df_trains['OnTime'] / df_trains['Total'] * 100).round(1)

            fig_trains = go.Figure()

            fig_trains.add_trace(go.Bar(
                y=df_trains['LineName'],
                x=df_trains['OnTime'],
                name='On Time',
                orientation='h',
                marker=dict(color='#4CAF50'),
                text=df_trains['OnTime'],
                textposition='inside'
            ))

            fig_trains.add_trace(go.Bar(
                y=df_trains['LineName'],
                x=df_trains['Delayed'],
                name='Delayed',
                orientation='h',
                marker=dict(color='#f44336'),
                text=df_trains['Delayed'],
                textposition='inside'
            ))

            fig_trains.update_layout(
                barmode='stack',
                height=400,
                xaxis_title='Vehicles',
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig_trains, use_container_width=True)

            # Train performance table
            display_df = df_trains[['LineName', 'Total', 'OnTime', 'Delayed', 'OnTimeRate']].sort_values('OnTimeRate', ascending=False)
            st.dataframe(display_df, use_container_width=True, height=200)

    with col2:
        st.subheader("Top 10 Bus Routes")
        if go_lines_buses:
            df_buses = pd.DataFrame(go_lines_buses)
            df_buses['RouteName'] = df_buses['Code'].apply(get_route_name)
            df_buses['OnTimeRate'] = (df_buses['OnTime'] / df_buses['Total'] * 100).round(1)

            df_top_buses = df_buses.nlargest(10, 'Total')

            fig_buses = go.Figure()

            fig_buses.add_trace(go.Scatter(
                x=df_top_buses['Total'],
                y=df_top_buses['OnTimeRate'],
                mode='markers+text',
                text=df_top_buses['Code'],
                textposition='top center',
                marker=dict(
                    size=df_top_buses['Total'],
                    color=df_top_buses['OnTimeRate'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="On-Time %"),
                    sizemode='diameter',
                    sizeref=2,
                    line=dict(color='white', width=2)
                ),
                hovertemplate='<b>%{text}</b><br>Total: %{x}<br>On-Time: %{y:.1f}%<extra></extra>'
            ))

            fig_buses.update_layout(
                title='Bus Volume vs Performance (bubble size = total buses)',
                height=400,
                xaxis_title='Total Buses',
                yaxis_title='On-Time Rate %',
                yaxis_range=[0, 105]
            )

            st.plotly_chart(fig_buses, use_container_width=True)

            # Bus performance table
            display_df = df_top_buses[['RouteName', 'Total', 'OnTime', 'Delayed', 'OnTimeRate']].sort_values('Total', ascending=False)
            st.dataframe(display_df, use_container_width=True, height=200)

    st.markdown("---")

# ============================================================================
# KEY INSIGHTS
# ============================================================================
if show_insights:
    st.header("💡 Key Insights & Recommendations")

    insights_col1, insights_col2 = st.columns(2)

    with insights_col1:
        st.markdown("""
        <div style='background: #242629; padding: 25px; border-radius: 8px; border: 1px solid #2e3034; box-shadow: 0 1px 2px rgba(0,0,0,0.3);'>
            <h3 style='color: #d8d9da; margin-top: 0;'>📊 Performance Insights</h3>
            <ul style='color: #9fa3a8; line-height: 1.8;'>
                <li>Average performance: <b style='color: #d8d9da;'>{:.1f}%</b> <span style='color: {};'>{}</span> vs 95% target</li>
                <li>Best performance day: <b style='color: #73bf69;'>{:.1f}%</b></li>
                <li>Performance trend: <b style='color: {};'>{:+.1f}%</b> over period</li>
                <li>Consistency (lower is better): <b style='color: #d8d9da;'>{:.2f}σ</b></li>
            </ul>
        </div>
        """.format(
            avg_performance,
            "#73bf69" if avg_performance >= 95 else "#ff5705",
            "✅ Above" if avg_performance >= 95 else "⚠️ Below",
            df_history['performance'].max(),
            "#73bf69" if performance_trend >= 0 else "#ff5705",
            performance_trend,
            df_history['performance'].std()
        ), unsafe_allow_html=True)

    with insights_col2:
        st.markdown("""
        <div style='background: #242629; padding: 25px; border-radius: 8px; border: 1px solid #2e3034; box-shadow: 0 1px 2px rgba(0,0,0,0.3);'>
            <h3 style='color: #d8d9da; margin-top: 0;'>🎯 Recommendations</h3>
            <ul style='color: #9fa3a8; line-height: 1.8;'>
                <li>Focus on routes with <80% on-time rate</li>
                <li>Peak hour performance needs attention</li>
                <li>Monitor high-volume routes closely</li>
                <li>Investigate outlier delay days</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

st.caption("📡 Analytics updated every hour • Historical data simulated for demonstration")
