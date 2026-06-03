# Paris Cycling Traffic Dashboard

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

An interactive Streamlit dashboard exploring Paris cycling activity, from commute peaks to weather patterns and urban counter coverage.

**Live app:** https://paris-cycling-dashboard-sw82zmv87tc5sxqluddjrj.streamlit.app/

![Paris Cycling Dashboard introduction](assets/paris-cycling-hero.jpg)

## Project Overview

Cycling has become a central part of Paris mobility, but demand is not evenly distributed across the city. This project uses Paris bicycle counter data enriched with weather, school-holiday, and arrondissement context to understand when cycling traffic is strongest and whether counter coverage reflects observed demand.

The dashboard is designed as both an analytical portfolio project and a practical urban-mobility monitoring tool.

## Key Questions

- When does cycling traffic peak during the day?
- How do weekday and weekend cycling patterns differ?
- Do school holidays change cycling volume?
- How are rain, snowfall, and temperature linked with bicycle counts?
- Which arrondissements show gaps between cycling demand and counter coverage?

## Data Sources

The analysis combines three data layers:

| Dataset | Role in the project |
| --- | --- |
| Paris cycling traffic | Hourly bicycle counts by counter meter, timestamp, and location |
| Weather context | Temperature, precipitation, weather codes, and simplified weather categories |
| School holiday calendar | Holiday flags used to compare normal and school-holiday travel patterns |

The full enriched dataset contains **947,231 counter-hour records** and **24 final columns**. Because the full file is too large for a normal GitHub repository, the deployed app uses deployment-safe CSV exports while preserving the analytical fields needed for the dashboard.

## Dashboard Highlights

- KPI summary of total cycling count, counter meters, and Paris arrondissement scope
- Overview of commuting peaks and notebook findings
- Interactive map showing counter coverage by arrondissement
- Hourly and calendar-based cycling pattern analysis
- Weather and school-holiday comparison views
- Compact recommendations for improving counter placement

## Main Findings

- Cycling traffic has clear morning and evening commuting peaks.
- Weekday traffic is stronger than weekend traffic.
- School holidays reduce cycling volume, especially during commute periods.
- Rain and snowfall are linked with lower cycling counts.
- Counter meters are not evenly distributed across Paris.
- Some busy central areas appear under-covered because their traffic share is higher than their meter share.

## Recommendations

- Add counters in high-traffic under-covered areas, especially the 3rd, 7th, 10th, and 11th arrondissements.
- Use weather and school-holiday patterns when interpreting short-term drops in cycling volume.
- Combine counter coverage with cycling infrastructure data before deciding where to expand monitoring.

## Repository Structure

```text
app.py                                  Streamlit dashboard
assets/paris-cycling-hero.jpg           Dashboard introduction image
data/streamlit_public_traffic.csv       Deployment-safe traffic extract
data/cycling_traffic_summary.csv        Arrondissement coverage summary
powerbi/                                Power BI-ready exports and notes
scripts/                                Data preparation and export scripts
requirements.txt                        Python dependencies
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

## Rebuild The Data

The full raw source files are not included in this repository. To rebuild the enriched dataset locally, place the raw source files in a local `raw/` folder, or set `CYCLING_SOURCE_DIR` to the folder containing them.

Then run:

```bash
python scripts/build_traffic_enriched.py
python scripts/export_streamlit_public_data.py
python scripts/export_powerbi_map_data.py
```

## Power BI Exports

The `powerbi/` folder contains CSV files and notes for building a related map report in Power BI:

- `powerbi_map_counter_locations.csv`
- `powerbi_arrondissement_coverage.csv`
- `powerbi_daily_arrondissement_traffic.csv`
- `measures.dax`
- `paris_cycling_theme.json`

## Tech Stack

- Python
- Pandas
- Streamlit
- Plotly
- Power BI

## Authors

- Stefania Licciardi
- Victoria Ford
- Sascha Behrens

Data Analytics Bootcamp project.
