"""
EV Fleet Battery Data Simulator
Generates realistic battery telemetry for a mixed electric vehicle fleet.
Simulates: electric forklifts, delivery vans, cargo bikes, e-scooters.
Author: Prateek Gaur — github.com/PRATdoppelEK
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

VEHICLE_TYPES = {
    "forklift": {
        "count": 8, "capacity_ah": 500, "nominal_voltage": 48.0,
        "cycles_per_day": 2, "typical_dod": 0.75,
        "degradation_rate": 0.0002, "prefix": "FLT",
    },
    "delivery_van": {
        "count": 6, "capacity_ah": 200, "nominal_voltage": 400.0,
        "cycles_per_day": 1, "typical_dod": 0.85,
        "degradation_rate": 0.00015, "prefix": "VAN",
    },
    "cargo_bike": {
        "count": 10, "capacity_ah": 15, "nominal_voltage": 48.0,
        "cycles_per_day": 3, "typical_dod": 0.90,
        "degradation_rate": 0.0003, "prefix": "CBK",
    },
    "escooter": {
        "count": 16, "capacity_ah": 7, "nominal_voltage": 48.0,
        "cycles_per_day": 4, "typical_dod": 0.95,
        "degradation_rate": 0.0004, "prefix": "SCT",
    },
}

FAULT_SCENARIOS = [
    "cell_degradation", "thermal_runaway_risk",
    "capacity_fade", "internal_resistance_rise",
    "normal", "normal", "normal", "normal", "normal",
]


def generate_fleet(seed=42):
    """Generate a complete simulated EV fleet with battery telemetry."""
    np.random.seed(seed)
    random.seed(seed)
    vehicles = []
    vehicle_id = 1

    for vtype, config in VEHICLE_TYPES.items():
        for i in range(config["count"]):
            vid = config["prefix"] + "_" + str(vehicle_id).zfill(3)
            age_days = random.randint(180, 1460)
            total_cycles = int(age_days * config["cycles_per_day"] * random.uniform(0.7, 1.0))
            soh = max(0.60, 1.0 - total_cycles * config["degradation_rate"] * random.uniform(0.8, 1.2))
            soc = random.uniform(0.15, 0.95)
            temperature = round(random.uniform(15, 35) + random.uniform(2, 12) + np.random.normal(0, 1), 1)
            r_base = 0.005 + (1.0 - soh) * 0.015
            resistance = round(r_base * random.uniform(0.9, 1.1), 4)
            ocv = config["nominal_voltage"] * (0.90 + soc * 0.12)
            current = random.uniform(-config["capacity_ah"] * 0.3, config["capacity_ah"] * 0.5)
            voltage = round(ocv - current * resistance + np.random.normal(0, 0.05), 2)

            fault = random.choice(FAULT_SCENARIOS)
            if soh < 0.72:
                fault = "capacity_fade"
            if temperature > 42:
                fault = "thermal_runaway_risk"
            if resistance > 0.018:
                fault = "internal_resistance_rise"

            cycles_to_eol = int((soh - 0.80) / config["degradation_rate"]) if soh > 0.80 else 0

            if fault == "thermal_runaway_risk":
                status = "CRITICAL"
            elif fault in ["cell_degradation", "internal_resistance_rise"] or soh < 0.72:
                status = "WARNING"
            elif soh < 0.80:
                status = "REPLACE_SOON"
            elif soc < 0.15:
                status = "LOW_BATTERY"
            else:
                status = "HEALTHY"

            minutes_ago = random.randint(0, 120)
            last_seen = (datetime.now() - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M")

            vehicles.append({
                "vehicle_id": vid, "vehicle_type": vtype,
                "age_days": age_days, "total_cycles": total_cycles,
                "soh": round(soh, 3), "soc": round(soc, 3),
                "voltage_v": voltage, "current_a": round(current, 2),
                "temperature_c": temperature, "resistance_ohm": resistance,
                "fault_type": fault, "status": status,
                "cycles_to_eol": cycles_to_eol,
                "capacity_ah": config["capacity_ah"],
                "nominal_voltage": config["nominal_voltage"],
                "last_seen": last_seen,
            })
            vehicle_id += 1

    return pd.DataFrame(vehicles)


def get_fleet_summary(df):
    """Return a summary dictionary of fleet health metrics."""
    total = len(df)
    return {
        "total_vehicles": total,
        "critical": len(df[df["status"] == "CRITICAL"]),
        "warning": len(df[df["status"] == "WARNING"]),
        "replace_soon": len(df[df["status"] == "REPLACE_SOON"]),
        "healthy": len(df[df["status"] == "HEALTHY"]),
        "low_battery": len(df[df["status"] == "LOW_BATTERY"]),
        "avg_soh": round(df["soh"].mean(), 3),
        "avg_soc": round(df["soc"].mean(), 3),
        "avg_temp_c": round(df["temperature_c"].mean(), 1),
        "min_soh": round(df["soh"].min(), 3),
        "fleet_health_score": round((len(df[df["status"] == "HEALTHY"]) / total) * 100, 1),
    }


if __name__ == "__main__":
    df = generate_fleet()
    s = get_fleet_summary(df)
    print("Fleet: " + str(s["total_vehicles"]) + " vehicles")
    print("Critical: " + str(s["critical"]) + "  Warning: " + str(s["warning"]) + "  Healthy: " + str(s["healthy"]))
    print("Fleet health score: " + str(s["fleet_health_score"]) + "%")
    df.to_csv("fleet_snapshot.csv", index=False)
    print("Saved to fleet_snapshot.csv")
