# Paris Cycling Traffic Dashboard

Interactive Streamlit dashboard for exploring bicycle counter traffic in Paris.

The project analyzes hourly cycling counts enriched with weather, calendar, school-holiday, and arrondissement coverage context. It is designed as a public portfolio dashboard for LinkedIn and GitHub.

## Live Dashboard

Add your Streamlit Community Cloud URL here after deployment:

```text
https://your-app-name.streamlit.app
```

## Features

- KPI overview of total and average cycling counts
- Hourly traffic patterns and weekday/weekend comparison
- School holiday and weather impact analysis
- Interactive map of cycling activity and coverage status
- Arrondissement coverage analysis, including missing-data areas
- Power BI-ready map exports in `powerbi/`

## Data

The deployed dashboard uses:

```text
data/streamlit_public_traffic.csv
data/cycling_traffic_summary.csv
```

`streamlit_public_traffic.csv` is an aggregated public extract created from the full local enriched dataset. The full local file, `data/traffic_enriched.csv`, is intentionally ignored by Git because it is too large for a normal GitHub push.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy To Streamlit Community Cloud

1. Create a GitHub repository, for example `paris-cycling-dashboard`.
2. Push this project folder to GitHub.
3. Go to https://share.streamlit.io.
4. Click **Create app**.
5. Select your repository, branch, and `app.py`.
6. Deploy and copy the public URL.

## Suggested LinkedIn Caption

I built an interactive Streamlit dashboard analyzing cycling traffic patterns in Paris using bicycle counter data enriched with weather, school holiday, and arrondissement coverage context.

The dashboard highlights commuting peaks, weekday/weekend differences, weather impacts, and gaps in cycling counter coverage across Paris.

Tools: Python, Pandas, Streamlit, Plotly, Power BI, geospatial analysis.
