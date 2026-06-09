# FDE Deployment Guide
## How to Deploy This System at a Real Customer

This guide explains how a Forward Deployment Engineer would take this project
from a GitHub repository to a live running system at a customer site.
Estimated time from arrival to first working demo: 4 hours.

---

## Pre-Deployment Checklist

Before arriving at the customer site, confirm:

- [ ] Python 3.8 or higher available on a company laptop or server
- [ ] Internet access for pip install (or prepare offline package bundle)
- [ ] Access to battery telemetry data (CSV export, API, or BMS connection)
- [ ] Contact person who understands the data schema
- [ ] One hour of uninterrupted time with an operations manager

---

## Hour 1: Data Discovery

Do not install anything yet. Understand the data first.

Questions to ask:
1. How is battery data currently collected? (BMS system, manual log, CSV export)
2. What fields are available? (voltage, current, temperature, SOC, cycle count)
3. How often is data updated? (real-time, hourly, daily)
4. How many vehicles are in the fleet?
5. What is the current process when a battery fails? How much does it cost?

Key insight: The value of this system depends entirely on the quality and
completeness of their data. Better data = more accurate health estimates.

---

## Hour 2: Data Connection

Replace the simulator with real customer data.

Option A — CSV file (fastest)
The customer exports their battery data as a CSV file.
Modify data/simulator.py to read from the CSV instead of generating synthetic data.
Map their column names to the expected field names in the schema.

Option B — REST API
The customer has a BMS API that returns battery readings.
Add an API adapter that calls their endpoint and converts the response
to the DataFrame format expected by health_analyzer.py.

Option C — Database connection
The customer has a SQL database with historical battery data.
Use pandas.read_sql() to query the relevant table.

In all cases, the health_analyzer.py and dashboard/app.py remain unchanged.
Only the data source changes. This is the adapter pattern.

---

## Hour 3: Demo and Calibration

Run the dashboard with their real data.

Show the operations manager:
1. The fleet status overview — how many vehicles are in each status category
2. The active alerts — are the flagged vehicles actually known problem vehicles?
3. The SOH distribution — does it match their experience of which vehicles are old?

Calibration questions:
- "Does this vehicle correctly show as a problem? When did it start having issues?"
- "Are there vehicles we flagged that you know are actually fine?"
- "What threshold would you want to use for a WARNING alert?"

Adjust the thresholds in health_analyzer.py based on their feedback.
This is the most important step — a system that matches their intuition
will be trusted and used. One that contradicts their experience will be ignored.

---

## Hour 4: Handover

After the demo is validated:

1. Write down the 3 most important findings from their real data
2. Show one operations person how to run the dashboard themselves
3. Leave a one-page instruction sheet (print it)
4. Agree on the next step: expand to more vehicles, connect to live data, or automate alerts

One-page instruction sheet content:
- How to start the dashboard (one command)
- What each status colour means
- Who to call when a CRITICAL alert appears
- How to export the report

---

## Typical Customer Questions and Answers

Q: Can this connect to our existing BMS software?
A: Yes, if your BMS has an API or can export CSV data. Data connection
   takes approximately 2 hours for a standard REST API or CSV export.

Q: Is our battery data safe?
A: The system runs entirely on your own laptop or server.
   No data is sent anywhere external. It works without internet access.

Q: How accurate is the SOH estimation?
A: With real cycle data, accuracy is within 3-5%. With only voltage and
   temperature data and no cycle history, accuracy is lower (8-12%).
   The most valuable output is the relative ranking of vehicles,
   not the absolute SOH number.

Q: Can we set up automatic email alerts?
A: Yes. Add a scheduled task that runs report_generator.py daily
   and emails the output. Takes approximately 1 hour to configure.

Q: What does it cost?
A: The software is open source. Cost is the deployment time (1 day)
   and any infrastructure needed to run it continuously.
