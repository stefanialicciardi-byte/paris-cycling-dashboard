# Data

This folder contains deployment-safe CSV files used by the Streamlit dashboard.

## Included In Git

- `streamlit_public_traffic.csv`: aggregated public extract used by `app.py`.
- `cycling_traffic_summary.csv`: arrondissement-level coverage summary.

## Ignored Locally

- `traffic_enriched.csv`: full enriched dataset with 947,231 rows. It is intentionally excluded from Git because it is too large for a normal GitHub repository.
- `cycling_clean_sample.csv`: small local demo sample kept for fallback testing.

## Arrondissement Coverage

The source traffic records cover 15 arrondissements:

```text
1, 3, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 17, 19, 20
```

The dashboard coverage table includes all 20 Paris arrondissements and marks missing arrondissements as `No data`.
