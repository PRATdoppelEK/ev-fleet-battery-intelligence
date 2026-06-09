"""
Battery Health Analyser
Computes SOH status, RUL estimation, anomaly flags, and maintenance priority.
Author: Prateek Gaur — github.com/PRATdoppelEK
"""

import pandas as pd
import numpy as np


STATUS_COLORS = {
    "CRITICAL":     "#CC0000",
    "WARNING":      "#FF8800",
    "REPLACE_SOON": "#FFCC00",
    "LOW_BATTERY":  "#1A52C8",
    "HEALTHY":      "#1A7A3C",
}

STATUS_PRIORITY = {
    "CRITICAL": 1, "WARNING": 2, "REPLACE_SOON": 3,
    "LOW_BATTERY": 4, "HEALTHY": 5,
}


def compute_rul_days(row):
    """Estimate remaining useful life in days based on current degradation rate."""
    if row["soh"] <= 0.80:
        return 0
    deg_rate = row["degradation_rate"] if "degradation_rate" in row else 0.0002
    cycles_left = row["cycles_to_eol"]
    cycles_per_day = 2 if row["vehicle_type"] == "forklift" else (
        1 if row["vehicle_type"] == "delivery_van" else (
        3 if row["vehicle_type"] == "cargo_bike" else 4))
    if cycles_per_day == 0:
        return 999
    return int(cycles_left / cycles_per_day)


def classify_maintenance_action(row):
    """Determine recommended maintenance action."""
    if row["status"] == "CRITICAL":
        return "IMMEDIATE STOP — Remove from service now"
    elif row["status"] == "WARNING":
        return "Schedule inspection within 48 hours"
    elif row["status"] == "REPLACE_SOON":
        return "Plan battery replacement within 30 days"
    elif row["status"] == "LOW_BATTERY":
        return "Return to charging station"
    else:
        return "No action required"


def analyse_fleet(df):
    """Run full health analysis on fleet DataFrame."""
    df = df.copy()
    df["rul_days"] = df.apply(compute_rul_days, axis=1)
    df["maintenance_action"] = df.apply(classify_maintenance_action, axis=1)
    df["priority_score"] = df["status"].map(STATUS_PRIORITY)
    df["status_color"] = df["status"].map(STATUS_COLORS)

    # SOH health band
    def soh_band(soh):
        if soh >= 0.90:
            return "Excellent"
        elif soh >= 0.80:
            return "Good"
        elif soh >= 0.70:
            return "Degraded"
        else:
            return "End of Life"

    df["soh_band"] = df["soh"].apply(soh_band)

    # Temperature risk
    df["temp_risk"] = df["temperature_c"].apply(
        lambda t: "HIGH" if t > 45 else ("MODERATE" if t > 38 else "NORMAL"))

    return df.sort_values("priority_score")


def get_alerts(df):
    """Return list of active alerts sorted by severity."""
    alerts = []
    for _, row in df[df["status"].isin(["CRITICAL", "WARNING"])].iterrows():
        alerts.append({
            "vehicle_id": row["vehicle_id"],
            "vehicle_type": row["vehicle_type"].replace("_", " ").title(),
            "status": row["status"],
            "fault": row["fault_type"].replace("_", " ").title(),
            "soh": row["soh"],
            "temperature_c": row["temperature_c"],
            "action": row["maintenance_action"],
        })
    return sorted(alerts, key=lambda x: STATUS_PRIORITY.get(x["status"], 9))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "..")
    from data.simulator import generate_fleet
    df = generate_fleet()
    df_analysed = analyse_fleet(df)
    alerts = get_alerts(df_analysed)
    print("Active alerts: " + str(len(alerts)))
    for a in alerts[:5]:
        print("  " + a["vehicle_id"] + " | " + a["status"] + " | " + a["fault"] + " | SOH: " + str(a["soh"]))
