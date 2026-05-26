# Paris Cycling Power BI Map Dashboard

This folder contains Power BI-ready extracts for a cycling traffic map dashboard.

## Files

- `powerbi_map_counter_locations.csv`: one row per counter location, with latitude, longitude, traffic volume, weather averages, and coverage status.
- `powerbi_arrondissement_coverage.csv`: all 20 Paris arrondissements, including missing traffic areas marked as `No data`.
- `powerbi_daily_arrondissement_traffic.csv`: daily traffic totals by arrondissement for date trend visuals and slicers.
- `measures.dax`: suggested Power BI measures.
- `paris_cycling_theme.json`: optional Power BI theme.

## Build The Map Page

1. Open Power BI Desktop.
2. Get Data > Text/CSV and load:
   - `powerbi_map_counter_locations.csv`
   - `powerbi_arrondissement_coverage.csv`
   - `powerbi_daily_arrondissement_traffic.csv`
3. In Model view, create relationships:
   - `powerbi_map_counter_locations[arrondissement]` to `powerbi_arrondissement_coverage[arrondissement]`
   - `powerbi_daily_arrondissement_traffic[arrondissement]` to `powerbi_arrondissement_coverage[arrondissement]`
4. Set data categories:
   - `latitude`: Latitude
   - `longitude`: Longitude
   - `arrondissement`: Place or Uncategorized
5. Optional: View > Themes > Browse for themes > select `paris_cycling_theme.json`.

## Recommended Dashboard Layout

Top KPI cards:
- `Total Countings`
- `Average Hourly Count`
- `Counter Locations`
- `Under-covered Arrondissements`
- `No Data Arrondissements`

Main map:
- Visual: Azure Maps or Map
- Latitude: `latitude`
- Longitude: `longitude`
- Bubble size: `total_hourly_countings`
- Legend: `coverage_status`
- Tooltips: `meter_name`, `arrondissement_label`, `avg_hourly_countings`, `meters_vs_hourly_gap_pct`, `avg_temperature`, `avg_precipitation`

Side visuals:
- Bar chart: `arrondissement_label` by `meters_vs_hourly_gap_pct`, colored by `coverage_status`
- Line chart: `date` by `daily_countings`
- Slicers: `coverage_status`, `arrondissement_label`, `year`, `month`

## Coverage Interpretation

- `Under-covered`: the arrondissement's share of meters is lower than its share of recorded cycling traffic.
- `Over-covered`: the arrondissement's share of meters is higher than its share of recorded cycling traffic.
- `No data`: no counter records are present in the full traffic dataset for that arrondissement.
