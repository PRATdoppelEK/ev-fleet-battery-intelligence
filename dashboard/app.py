"""
EV Fleet Battery Intelligence Dashboard
Streamlit web dashboard for real-time fleet battery monitoring.
Author: Prateek Gaur — github.com/PRATdoppelEK

Run: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.simulator import generate_fleet, get_fleet_summary
from models.health_analyzer import analyse_fleet, get_alerts

# ── PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="EV Fleet Battery Intelligence",
    page_icon="favicon.ico" if os.path.exists("favicon.ico") else "🔋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM STYLE ──────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #1A1C28; border-radius: 8px;
        padding: 16px; text-align: center; margin: 4px;
    }
    .metric-value { font-size: 2rem; font-weight: 700; }
    .metric-label { font-size: 0.8rem; color: #9090A8; margin-top: 4px; }
    .alert-critical { background: #2A1414; border-left: 4px solid #CC0000;
        padding: 10px 14px; border-radius: 0 6px 6px 0; margin: 4px 0; }
    .alert-warning { background: #2A1E0A; border-left: 4px solid #FF8800;
        padding: 10px 14px; border-radius: 0 6px 6px 0; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────
st.sidebar.title("Fleet Intelligence")
st.sidebar.markdown("**EV Battery Monitor**")
st.sidebar.markdown("---")

vehicle_filter = st.sidebar.multiselect(
    "Vehicle Type",
    ["forklift", "delivery_van", "cargo_bike", "escooter"],
    default=["forklift", "delivery_van", "cargo_bike", "escooter"],
    format_func=lambda x: x.replace("_", " ").title()
)

status_filter = st.sidebar.multiselect(
    "Status Filter",
    ["CRITICAL", "WARNING", "REPLACE_SOON", "LOW_BATTERY", "HEALTHY"],
    default=["CRITICAL", "WARNING", "REPLACE_SOON", "LOW_BATTERY", "HEALTHY"]
)

soh_min = st.sidebar.slider("Min SOH", 0.0, 1.0, 0.0, 0.01)

st.sidebar.markdown("---")
if st.sidebar.button("Refresh Data"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Built by **Prateek Gaur**")
st.sidebar.markdown("[GitHub](https://github.com/PRATdoppelEK)")

# ── LOAD DATA ─────────────────────────────────────────────────────
import random
seed = random.randint(1, 999)

@st.cache_data(ttl=30)
def load_data(s):
    df_raw = generate_fleet(seed=s)
    df = analyse_fleet(df_raw)
    return df

df = load_data(42)
summary = get_fleet_summary(df)
alerts = get_alerts(df)

# Apply filters
df_filtered = df[
    (df["vehicle_type"].isin(vehicle_filter)) &
    (df["status"].isin(status_filter)) &
    (df["soh"] >= soh_min)
]

# ── HEADER ────────────────────────────────────────────────────────
st.title("EV Fleet Battery Intelligence")
st.markdown("Real-time battery health monitoring across your electric vehicle fleet.")
st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric("Total Vehicles", summary["total_vehicles"])
with c2:
    st.metric("CRITICAL", summary["critical"],
              delta=None, delta_color="inverse")
with c3:
    st.metric("WARNING", summary["warning"])
with c4:
    st.metric("Avg SOH", str(round(summary["avg_soh"] * 100, 1)) + "%")
with c5:
    st.metric("Avg SOC", str(round(summary["avg_soc"] * 100, 1)) + "%")
with c6:
    st.metric("Fleet Health", str(summary["fleet_health_score"]) + "%")

st.markdown("---")

# ── ALERTS ────────────────────────────────────────────────────────
if alerts:
    st.subheader("Active Alerts (" + str(len(alerts)) + ")")
    for alert in alerts[:8]:
        color = "#CC0000" if alert["status"] == "CRITICAL" else "#FF8800"
        st.markdown(
            "<div style='background:#1A1C28; border-left: 4px solid " + color + "; "
            "padding:10px 14px; border-radius:0 6px 6px 0; margin:4px 0;'>"
            "<b style='color:" + color + ";'>" + alert["status"] + "</b> — "
            "<b>" + alert["vehicle_id"] + "</b> (" + alert["vehicle_type"] + ") | "
            "Fault: " + alert["fault"] + " | SOH: " + str(round(alert["soh"] * 100, 1)) + "% | "
            "Temp: " + str(alert["temperature_c"]) + "C | "
            "<i>" + alert["action"] + "</i>"
            "</div>",
            unsafe_allow_html=True
        )
    st.markdown("")

# ── CHARTS ROW 1 ──────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Fleet Status Distribution")
    status_counts = df_filtered["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    color_map = {
        "CRITICAL": "#CC0000", "WARNING": "#FF8800",
        "REPLACE_SOON": "#FFCC00", "LOW_BATTERY": "#1A52C8",
        "HEALTHY": "#1A7A3C"
    }
    fig_status = px.pie(
        status_counts, values="Count", names="Status",
        color="Status", color_discrete_map=color_map,
        hole=0.4
    )
    fig_status.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.subheader("SOH Distribution by Vehicle Type")
    fig_soh = px.box(
        df_filtered, x="vehicle_type", y="soh",
        color="vehicle_type",
        labels={"vehicle_type": "Vehicle Type", "soh": "State of Health"},
    )
    fig_soh.add_hline(y=0.80, line_dash="dash", line_color="red",
                      annotation_text="EOL threshold (80%)")
    fig_soh.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", showlegend=False,
        margin=dict(t=20, b=20),
        xaxis=dict(ticktext=["Forklift", "Delivery Van", "Cargo Bike", "E-Scooter"],
                   tickvals=["forklift", "delivery_van", "cargo_bike", "escooter"])
    )
    st.plotly_chart(fig_soh, use_container_width=True)

# ── CHARTS ROW 2 ──────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("SOC vs SOH — All Vehicles")
    fig_scatter = px.scatter(
        df_filtered, x="soc", y="soh",
        color="status", color_discrete_map=color_map,
        hover_data=["vehicle_id", "vehicle_type", "temperature_c", "fault_type"],
        labels={"soc": "State of Charge", "soh": "State of Health"},
        size_max=8,
    )
    fig_scatter.add_hline(y=0.80, line_dash="dash", line_color="red",
                          annotation_text="EOL threshold")
    fig_scatter.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col4:
    st.subheader("Temperature Distribution")
    fig_temp = px.histogram(
        df_filtered, x="temperature_c", color="status",
        color_discrete_map=color_map, nbins=20,
        labels={"temperature_c": "Temperature (C)"},
    )
    fig_temp.add_vline(x=45, line_dash="dash", line_color="red",
                       annotation_text="Critical threshold")
    fig_temp.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_temp, use_container_width=True)

# ── FLEET TABLE ───────────────────────────────────────────────────
st.markdown("---")
st.subheader("Fleet Detail — " + str(len(df_filtered)) + " vehicles")

display_cols = [
    "vehicle_id", "vehicle_type", "status", "soh", "soc",
    "temperature_c", "fault_type", "rul_days", "maintenance_action", "last_seen"
]

df_display = df_filtered[display_cols].copy()
df_display.columns = [
    "ID", "Type", "Status", "SOH", "SOC",
    "Temp (C)", "Fault", "RUL (days)", "Action", "Last Seen"
]
df_display["SOH"] = (df_display["SOH"] * 100).round(1).astype(str) + "%"
df_display["SOC"] = (df_display["SOC"] * 100).round(1).astype(str) + "%"
df_display["Type"] = df_display["Type"].str.replace("_", " ").str.title()
df_display["Fault"] = df_display["Fault"].str.replace("_", " ").str.title()

st.dataframe(df_display, use_container_width=True, hide_index=True)

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "EV Fleet Battery Intelligence | Built by Prateek Gaur | "
    "[github.com/PRATdoppelEK](https://github.com/PRATdoppelEK) | "
    "Data refreshes every 30 seconds"
)
