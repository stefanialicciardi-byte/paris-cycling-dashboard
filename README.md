# Paris Cycling Traffic Dashboard

An interactive analytics dashboard exploring bicycle traffic patterns in Paris using counter data enriched with weather, school-holiday, and arrondissement coverage context.

Built as a portfolio project with **Python**, **Pandas**, **Streamlit**, **Plotly**, and **Power BI-ready geospatial exports**.

## Live Dashboard

Streamlit app:

```text
Add your Streamlit Community Cloud URL here after deployment.
```

## Project Overview

Paris has expanded cycling infrastructure significantly, but traffic monitoring is not evenly distributed across all arrondissements. This project investigates when cycling traffic is highest, how external factors such as weather and school holidays affect bicycle counts, and whether counter coverage aligns with recorded cycling demand.

The dashboard is designed for quick exploration by recruiters, stakeholders, and urban mobility teams.

## Key Questions

- When are the main cycling traffic peaks during the day?
- How do weekdays and weekends differ?
- Do school holidays reduce bicycle traffic?
- How does weather affect hourly cycling counts?
- Which arrondissements appear under-covered by counters?

## Dashboard Features

- KPI overview of total countings, average hourly counts, counter locations, and coverage.
- Hourly traffic profile with weekday/weekend comparison.
- School-holiday and weather impact analysis.
- Interactive map of cycling counter locations.
- Coverage gap analysis for all 20 Paris arrondissements.
- Power BI-ready CSV exports for map-based reporting.

## Data

The deployed app uses a GitHub-safe public extract:

```text
data/streamlit_public_traffic.csv
data/cycling_traffic_summary.csv
```

The original full enriched dataset has 947,231 rows and is kept out of Git because of file-size limits. The public extract preserves the dashboard analysis at an aggregated level suitable for deployment.

Important data note: the source traffic data includes records for 15 arrondissements. The coverage table displays all 20 Paris arrondissements and marks the missing five as `No data`.

To rebuild the full local enriched dataset, place the raw source files in an ignored `raw/` folder or set `CYCLING_SOURCE_DIR` to the folder containing them, then run:

```bash
python scripts/build_traffic_enriched.py
python scripts/export_streamlit_public_data.py
python scripts/export_powerbi_map_data.py
```

## Repository Structure

```text
.
├── app.py
├── data/
│   ├── streamlit_public_traffic.csv
│   └── cycling_traffic_summary.csv
├── powerbi/
│   ├── powerbi_map_counter_locations.csv
│   ├── powerbi_arrondissement_coverage.csv
│   ├── powerbi_daily_arrondissement_traffic.csv
│   ├── measures.dax
│   └── README_powerbi_map_dashboard.md
├── scripts/
│   ├── build_traffic_enriched.py
│   ├── export_streamlit_public_data.py
│   └── export_powerbi_map_data.py
├── requirements.txt
└── README.md
```

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Power BI

Power BI-ready exports are included in `powerbi/`. The main map file is:

```text
powerbi/powerbi_map_counter_locations.csv
```

Recommended Power BI map setup:

- Latitude: `latitude`
- Longitude: `longitude`
- Bubble size: `total_hourly_countings`
- Legend: `coverage_status`
- Tooltips: `meter_name`, `arrondissement_label`, `avg_hourly_countings`, `meters_vs_hourly_gap_pct`

## Deployment

This app can be deployed on Streamlit Community Cloud:

1. Push this repository to GitHub.
2. Go to https://share.streamlit.io.
3. Create a new app from this repository.
4. Select branch `main`.
5. Set the main file path to `app.py`.
6. Deploy and copy the public URL.

## Tools

- Python
- Pandas
- Streamlit
- Plotly
- Power BI
- Git / GitHub

## Author

Stefania Licciardi
