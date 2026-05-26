from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FULL_PATH = DATA_DIR / "traffic_enriched.csv"
SUMMARY_PATH = DATA_DIR / "cycling_traffic_summary.csv"
OUTPUT_PATH = DATA_DIR / "streamlit_public_traffic.csv"


def load_coverage() -> pd.DataFrame:
    summary = pd.read_csv(SUMMARY_PATH)
    for col in [
        "area_share_pct",
        "meters_share_pct",
        "hourly_share_pct",
        "meter_vs_area_gap_pct",
        "meters_vs_hourly_gap_pct",
    ]:
        summary[col] = (
            summary[col].astype(str).str.replace("%", "", regex=False).astype(float)
        )
    summary["coverage_status"] = "Over-covered"
    summary.loc[summary["meters_vs_hourly_gap_pct"] < 0, "coverage_status"] = (
        "Under-covered"
    )
    return summary[["arrondissement", "coverage_status"]]


def main() -> None:
    usecols = [
        "date",
        "hour",
        "weekday",
        "is_weekend",
        "is_school_holiday",
        "arrondissement",
        "latitude",
        "longitude",
        "hourly_countings",
        "temperature",
        "precipitation",
        "weather_conditions",
    ]
    traffic = pd.read_csv(FULL_PATH, usecols=usecols, parse_dates=["date"])
    public = (
        traffic.groupby(
            [
                "date",
                "hour",
                "weekday",
                "is_weekend",
                "is_school_holiday",
                "arrondissement",
                "weather_conditions",
            ],
            as_index=False,
        )
        .agg(
            hourly_countings=("hourly_countings", "sum"),
            temperature=("temperature", "mean"),
            precipitation=("precipitation", "mean"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            counter_locations=("latitude", "size"),
        )
        .rename(
            columns={
                "is_school_holiday": "school_holiday",
                "weather_conditions": "weather_condition",
            }
        )
    )
    public = public.merge(load_coverage(), on="arrondissement", how="left")
    public["coverage_status"] = public["coverage_status"].fillna("No data")
    public.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(public):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
