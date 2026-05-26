from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "powerbi"

TRAFFIC_PATH = DATA_DIR / "traffic_enriched.csv"
SUMMARY_PATH = DATA_DIR / "cycling_traffic_summary.csv"

ARRONDISSEMENT_AREA_KM2 = {
    1: 1.83,
    2: 0.99,
    3: 1.17,
    4: 1.60,
    5: 2.54,
    6: 2.15,
    7: 4.09,
    8: 3.88,
    9: 2.18,
    10: 2.89,
    11: 3.67,
    12: 16.30,
    13: 7.15,
    14: 5.62,
    15: 8.48,
    16: 16.37,
    17: 5.67,
    18: 6.01,
    19: 6.79,
    20: 5.98,
}


def load_coverage_summary() -> pd.DataFrame:
    summary = pd.read_csv(SUMMARY_PATH)
    percent_cols = [
        "area_share_pct",
        "meters_share_pct",
        "hourly_share_pct",
        "meter_vs_area_gap_pct",
        "meters_vs_hourly_gap_pct",
    ]
    for col in percent_cols:
        summary[col] = (
            summary[col].astype(str).str.replace("%", "", regex=False).astype(float)
        )

    summary["arrondissement"] = summary["arrondissement"].astype(int)
    summary = (
        summary.set_index("arrondissement")
        .reindex(range(1, 21))
        .rename_axis("arrondissement")
        .reset_index()
    )
    summary[["n_rows", "n_meters", "total_hourly"]] = (
        summary[["n_rows", "n_meters", "total_hourly"]].fillna(0).astype(int)
    )
    summary["area_km2"] = summary["arrondissement"].map(ARRONDISSEMENT_AREA_KM2)

    total_area = summary["area_km2"].sum()
    total_meters = summary["n_meters"].sum()
    total_hourly = summary["total_hourly"].sum()
    summary["area_share_pct"] = summary["area_km2"] / total_area * 100
    summary["meters_share_pct"] = summary["n_meters"] / total_meters * 100
    summary["hourly_share_pct"] = summary["total_hourly"] / total_hourly * 100
    summary["meter_vs_area_gap_pct"] = (
        summary["meters_share_pct"] - summary["area_share_pct"]
    )
    summary["meters_vs_hourly_gap_pct"] = (
        summary["meters_share_pct"] - summary["hourly_share_pct"]
    )
    summary["arrondissement_label"] = summary["arrondissement"].astype(str) + "e"
    summary["coverage_status"] = "Over-covered"
    summary.loc[summary["meters_vs_hourly_gap_pct"] < 0, "coverage_status"] = (
        "Under-covered"
    )
    summary.loc[summary["n_rows"] == 0, "coverage_status"] = "No data"
    return summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    usecols = [
        "meter_id",
        "meter_name",
        "meter_site_identifier",
        "meter_site_name",
        "hourly_countings",
        "date",
        "hour",
        "weekday",
        "is_weekend",
        "month",
        "year",
        "is_school_holiday",
        "temperature",
        "precipitation",
        "weather_conditions",
        "arrondissement",
        "latitude",
        "longitude",
    ]
    traffic = pd.read_csv(TRAFFIC_PATH, usecols=usecols, parse_dates=["date"])
    coverage = load_coverage_summary()

    location = (
        traffic.groupby(
            [
                "meter_id",
                "meter_name",
                "meter_site_identifier",
                "meter_site_name",
                "arrondissement",
                "latitude",
                "longitude",
            ],
            as_index=False,
        )
        .agg(
            total_hourly_countings=("hourly_countings", "sum"),
            avg_hourly_countings=("hourly_countings", "mean"),
            max_hourly_countings=("hourly_countings", "max"),
            n_records=("hourly_countings", "size"),
            first_count_date=("date", "min"),
            last_count_date=("date", "max"),
            avg_temperature=("temperature", "mean"),
            avg_precipitation=("precipitation", "mean"),
        )
    )

    weekday = (
        traffic.groupby(["meter_id", "is_weekend"])["hourly_countings"]
        .mean()
        .unstack(fill_value=0)
        .rename(columns={False: "avg_weekday_countings", True: "avg_weekend_countings"})
        .reset_index()
    )
    location = location.merge(weekday, on="meter_id", how="left")

    weather = (
        traffic.pivot_table(
            index="meter_id",
            columns="weather_conditions",
            values="hourly_countings",
            aggfunc="mean",
        )
        .add_prefix("avg_weather_")
        .reset_index()
    )
    location = location.merge(weather, on="meter_id", how="left")

    location = location.merge(
        coverage[
            [
                "arrondissement",
                "arrondissement_label",
                "coverage_status",
                "meters_vs_hourly_gap_pct",
                "meter_vs_area_gap_pct",
                "area_share_pct",
                "meters_share_pct",
                "hourly_share_pct",
            ]
        ],
        on="arrondissement",
        how="left",
    )
    location["map_tooltip"] = (
        location["meter_name"]
        + " | "
        + location["arrondissement_label"]
        + " | "
        + location["coverage_status"]
    )

    daily = (
        traffic.groupby(["date", "arrondissement"], as_index=False)
        .agg(
            daily_countings=("hourly_countings", "sum"),
            avg_temperature=("temperature", "mean"),
            precipitation=("precipitation", "sum"),
        )
        .merge(
            coverage[["arrondissement", "arrondissement_label", "coverage_status"]],
            on="arrondissement",
            how="left",
        )
    )

    location.to_csv(OUT_DIR / "powerbi_map_counter_locations.csv", index=False)
    coverage.to_csv(OUT_DIR / "powerbi_arrondissement_coverage.csv", index=False)
    daily.to_csv(OUT_DIR / "powerbi_daily_arrondissement_traffic.csv", index=False)

    print("Exported:")
    print(f"- {OUT_DIR / 'powerbi_map_counter_locations.csv'} ({len(location):,} rows)")
    print(f"- {OUT_DIR / 'powerbi_arrondissement_coverage.csv'} ({len(coverage):,} rows)")
    print(f"- {OUT_DIR / 'powerbi_daily_arrondissement_traffic.csv'} ({len(daily):,} rows)")


if __name__ == "__main__":
    main()
