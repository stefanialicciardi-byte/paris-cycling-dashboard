# Paris Cycling Traffic Dashboard

This project explores bicycle traffic in Paris using public cycling counter data.
The dashboard looks at when cycling activity is highest, how it changes with
weather and school holidays, and whether counter coverage reflects where demand
is strongest.

**Streamlit app:** https://paris-cycling-dashboard-sw82zmv87tc5sxqluddjrj.streamlit.app/

![Paris Cycling Dashboard introduction](assets/paris-cycling-hero.jpg)

## Project Context

Cycling is an important part of mobility in Paris, but traffic is not evenly
distributed across days, hours, weather conditions, or arrondissements.

For this project, we started with Paris bicycle counter records and enriched
them with weather information, school-holiday dates, and arrondissement-level
coverage metrics. The goal was to build an interactive dashboard that helps
answer both traffic-pattern and sensor-coverage questions.

## Questions Explored

- At what times of day is cycling traffic highest?
- Are weekday and weekend patterns different?
- Does cycling volume change during school holidays?
- How are rain, snow, and temperature related to cycling counts?
- Which arrondissements appear to have lower counter coverage compared with their traffic share?

## Data Used

The analysis combines:

| Data | Purpose |
| --- | --- |
| Paris cycling traffic | Hourly bicycle counts by counter, timestamp, and location |
| Weather data | Temperature, precipitation, and weather categories |
| School holiday calendar | Holiday flags for comparing normal and holiday periods |
| Arrondissement coverage summary | Meter count, traffic share, area share, and coverage gap |

The full enriched dataset contains **947,231 counter-hour records**. Since this
file is too large to include in the repository, the deployed app uses exported
CSV files that keep the fields needed for the Streamlit dashboard.

## Dashboard Sections

- Introduction and project objective
- Data sources
- Data preparation
- Cycling patterns
- Weather impact
- Interactive dashboard with KPIs, charts, filters, and map
- Conclusion and recommendations

## Main Findings

- Cycling traffic shows clear morning and evening commute peaks.
- Weekday traffic is generally stronger than weekend traffic.
- School holidays reduce cycling volume, especially during commuting hours.
- Rain and snowfall are associated with lower cycling counts.
- Counter meters are not evenly distributed across Paris.
- Some central, high-traffic arrondissements appear under-covered compared with their traffic share.

## Recommendations

- Add counters in high-traffic under-covered areas, especially the 3rd, 7th, 10th, and 11th arrondissements.
- Use weather and school-holiday context when interpreting short-term drops in cycling traffic.
- Combine counter coverage with cycling infrastructure data before deciding where to expand monitoring.

## Repository Structure

```text
app.py                                  Streamlit dashboard
assets/paris-cycling-hero.jpg           Introduction image
data/streamlit_public_traffic.csv       CSV extract used by the app
data/cycling_traffic_summary.csv        Arrondissement coverage summary
powerbi/                                Power BI-ready exports
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

The full raw source files are not included in this repository. To rebuild the
enriched dataset locally, place the raw files in a local `raw/` folder, or set
`CYCLING_SOURCE_DIR` to the folder containing them.

Then run:

```bash
python scripts/build_traffic_enriched.py
python scripts/export_streamlit_public_data.py
python scripts/export_powerbi_map_data.py
```

## Tools

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
