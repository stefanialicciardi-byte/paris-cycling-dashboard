# Data

This folder contains deployment-safe CSV files used by the Streamlit dashboard.

## Included In Git

- `streamlit_public_traffic.csv`: aggregated public extract used by `app.py`.
- `cycling_traffic_summary.csv`: arrondissement-level coverage summary.

## Ignored Locally

- `traffic_enriched.csv`: full enriched dataset with 947,231 rows. It is intentionally excluded from Git because it is too large for a normal GitHub repository.
- `cycling_clean_sample.csv`: small local demo sample kept for fallback testing.

## Arrondissement Coverage

The dashboard presents Paris as a 20-arrondissement city context. The summary
CSV stores the arrondissement-level rows used for the current counter coverage
analysis, including meter counts, traffic share, area share, and coverage gap
metrics.
