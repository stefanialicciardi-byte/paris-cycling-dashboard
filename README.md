# Paris Cycling Traffic Dashboard

Interactive dashboard for exploring bicycle traffic patterns in Paris.

The project uses bicycle counter data enriched with weather, school-holiday, and arrondissement coverage information. The goal is to understand daily and weekly cycling patterns, identify the effect of external conditions, and evaluate whether counter coverage reflects where cycling activity is highest.

## Project Questions

- At which hours is cycling traffic highest?
- How do weekday and weekend patterns differ?
- Does cycling traffic change during school holidays?
- How does weather relate to bicycle counts?
- Which arrondissements appear under-covered by counting sensors?

## Dashboard

The Streamlit dashboard includes:

- Overview KPIs for cycling counts and counter coverage
- Hourly traffic trends
- Weekday vs weekend comparison
- School holiday analysis
- Weather impact analysis
- Interactive map of counter locations
- Arrondissement coverage gap analysis

## Data

The app uses two deployment-ready CSV files:

```text
data/streamlit_public_traffic.csv
data/cycling_traffic_summary.csv
```

The full enriched dataset contains 947,231 rows. Because the file is too large for a normal GitHub repository, the deployed version uses an aggregated extract that keeps the relevant fields for the dashboard.

The source traffic data contains records for 15 Paris arrondissements:

```text
1, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20
```

The coverage analysis still displays all 20 arrondissements. Arrondissements without records are marked as `No data`.

## Main Files

```text
app.py                                  Streamlit dashboard
data/streamlit_public_traffic.csv       Aggregated traffic data for deployment
data/cycling_traffic_summary.csv        Arrondissement coverage summary
powerbi/                                Power BI-ready map exports
scripts/                                Data preparation and export scripts
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

The full source files are not included in this repository. To rebuild the enriched dataset locally, place the raw source files in a local `raw/` folder, or set `CYCLING_SOURCE_DIR` to the folder containing them.

Then run:

```bash
python scripts/build_traffic_enriched.py
python scripts/export_streamlit_public_data.py
python scripts/export_powerbi_map_data.py
```

## Power BI Exports

The `powerbi/` folder contains CSV files for building a map report in Power BI:

- `powerbi_map_counter_locations.csv`
- `powerbi_arrondissement_coverage.csv`
- `powerbi_daily_arrondissement_traffic.csv`

Suggested map setup:

- Latitude: `latitude`
- Longitude: `longitude`
- Size: `total_hourly_countings`
- Legend: `coverage_status`
- Tooltip fields: `meter_name`, `arrondissement_label`, `avg_hourly_countings`, `meters_vs_hourly_gap_pct`

## Tools

- Python
- Pandas
- Streamlit
- Plotly
- Power BI

## Author

Stefania Licciardi
