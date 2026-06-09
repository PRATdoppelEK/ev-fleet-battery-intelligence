"""
EV Fleet Battery Intelligence — Quick Runner
Run this to start the dashboard or terminal demo.
Author: Prateek Gaur
"""

import sys
import os
import subprocess

def run_dashboard():
    print("")
    print("Starting EV Fleet Battery Intelligence Dashboard...")
    print("Open your browser at: http://localhost:8501")
    print("Press Ctrl+C to stop.")
    print("")
    subprocess.run(["streamlit", "run", "dashboard/app.py"])

def run_terminal():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from data.simulator import generate_fleet, get_fleet_summary
    from models.health_analyzer import analyse_fleet, get_alerts

    print("")
    print("EV FLEET BATTERY INTELLIGENCE")
    print("Author: Prateek Gaur — github.com/PRATdoppelEK")
    print("")

    df = generate_fleet()
    df = analyse_fleet(df)
    summary = get_fleet_summary(df)
    alerts = get_alerts(df)

    print("=" * 60)
    print("FLEET SUMMARY")
    print("=" * 60)
    print("Total vehicles   : " + str(summary["total_vehicles"]))
    print("CRITICAL         : " + str(summary["critical"]))
    print("WARNING          : " + str(summary["warning"]))
    print("Replace soon     : " + str(summary["replace_soon"]))
    print("Healthy          : " + str(summary["healthy"]))
    print("Average SOH      : " + str(round(summary["avg_soh"] * 100, 1)) + "%")
    print("Average SOC      : " + str(round(summary["avg_soc"] * 100, 1)) + "%")
    print("Fleet health     : " + str(summary["fleet_health_score"]) + "%")
    print("=" * 60)

    if alerts:
        print("")
        print("ACTIVE ALERTS (" + str(len(alerts)) + ")")
        print("-" * 60)
        for a in alerts:
            print(a["vehicle_id"] + " | " + a["status"] + " | " + a["fault"] + " | SOH: " + str(round(a["soh"]*100,1)) + "% | " + a["action"])
    else:
        print("No active alerts. All vehicles operating normally.")

    print("")
    print("Top 5 vehicles needing attention:")
    print("-" * 60)
    top5 = df.head(5)[["vehicle_id","vehicle_type","status","soh","temperature_c","maintenance_action"]]
    for _, row in top5.iterrows():
        print(row["vehicle_id"] + " (" + row["vehicle_type"] + ") | " +
              row["status"] + " | SOH: " + str(round(row["soh"]*100,1)) + "% | " +
              str(row["temperature_c"]) + "C")


if __name__ == "__main__":
    if "--terminal" in sys.argv:
        run_terminal()
    else:
        try:
            run_dashboard()
        except FileNotFoundError:
            print("Streamlit not found. Running terminal mode instead.")
            print("To install: pip3 install streamlit --break-system-packages")
            print("")
            run_terminal()
