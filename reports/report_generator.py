"""
Fleet Health Report Generator
Generates a text-based weekly fleet health report.
Author: Prateek Gaur — github.com/PRATdoppelEK

Usage: python3 reports/report_generator.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from data.simulator import generate_fleet, get_fleet_summary
from models.health_analyzer import analyse_fleet, get_alerts


def generate_report(df, summary, alerts):
    lines = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines.append("=" * 65)
    lines.append("EV FLEET BATTERY INTELLIGENCE REPORT")
    lines.append("Generated: " + now)
    lines.append("=" * 65)
    lines.append("")

    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 40)
    lines.append("Total vehicles monitored : " + str(summary["total_vehicles"]))
    lines.append("Fleet health score       : " + str(summary["fleet_health_score"]) + "%")
    lines.append("Average SOH              : " + str(round(summary["avg_soh"] * 100, 1)) + "%")
    lines.append("Average SOC              : " + str(round(summary["avg_soc"] * 100, 1)) + "%")
    lines.append("Average temperature      : " + str(summary["avg_temp_c"]) + " C")
    lines.append("")

    lines.append("STATUS BREAKDOWN")
    lines.append("-" * 40)
    lines.append("CRITICAL     : " + str(summary["critical"]) + " vehicles")
    lines.append("WARNING      : " + str(summary["warning"]) + " vehicles")
    lines.append("Replace Soon : " + str(summary["replace_soon"]) + " vehicles")
    lines.append("Low Battery  : " + str(summary["low_battery"]) + " vehicles")
    lines.append("Healthy      : " + str(summary["healthy"]) + " vehicles")
    lines.append("")

    if alerts:
        lines.append("ACTIVE ALERTS — IMMEDIATE ATTENTION REQUIRED")
        lines.append("-" * 40)
        for a in alerts:
            lines.append(a["vehicle_id"] + " | " + a["status"])
            lines.append("  Type   : " + a["vehicle_type"])
            lines.append("  Fault  : " + a["fault"])
            lines.append("  SOH    : " + str(round(a["soh"] * 100, 1)) + "%")
            lines.append("  Temp   : " + str(a["temperature_c"]) + " C")
            lines.append("  Action : " + a["action"])
            lines.append("")

    replace_df = df[df["status"] == "REPLACE_SOON"].sort_values("soh")
    if len(replace_df) > 0:
        lines.append("BATTERIES TO REPLACE WITHIN 30 DAYS")
        lines.append("-" * 40)
        for _, row in replace_df.iterrows():
            lines.append(row["vehicle_id"] + " | SOH: " + str(round(row["soh"]*100,1)) +
                         "% | RUL: " + str(row["rul_days"]) + " days")
        lines.append("")

    lines.append("RECOMMENDATIONS")
    lines.append("-" * 40)
    if summary["critical"] > 0:
        lines.append("1. Remove " + str(summary["critical"]) + " CRITICAL vehicle(s) from service immediately.")
    if summary["warning"] > 0:
        lines.append("2. Schedule inspection for " + str(summary["warning"]) + " WARNING vehicle(s) within 48 hours.")
    if summary["replace_soon"] > 0:
        lines.append("3. Procure " + str(summary["replace_soon"]) + " replacement battery pack(s) within 30 days.")
    if summary["avg_soh"] < 0.85:
        lines.append("4. Fleet average SOH is below 85%. Review charging protocols.")
    lines.append("")

    lines.append("=" * 65)
    lines.append("END OF REPORT")
    lines.append("=" * 65)

    return "\n".join(lines)


if __name__ == "__main__":
    df = generate_fleet()
    df = analyse_fleet(df)
    summary = get_fleet_summary(df)
    alerts = get_alerts(df)
    report = generate_report(df, summary, alerts)
    print(report)
    filename = "fleet_report_" + datetime.now().strftime("%Y%m%d") + ".txt"
    with open(filename, "w") as f:
        f.write(report)
    print("Report saved to: " + filename)
