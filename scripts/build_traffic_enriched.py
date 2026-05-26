from pathlib import Path

import pandas as pd
import requests
from sklearn.cluster import KMeans


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path("/Users/stefi/Downloads")
RAW_PATH = DOWNLOADS / "comptage-velo-donnees-compteurs (2).csv"
HOLIDAYS_PATH = DOWNLOADS / "paris_zone_c_school_holidays.csv"
WMO_PATH = DOWNLOADS / "wmo_weather_codes.csv"
LOOKUP_PATH = DOWNLOADS / "meter_arrondissment.csv"
OUTPUT_PATH = ROOT / "data" / "traffic_enriched.csv"

RAW_COLUMNS = [
    "Identifiant du compteur",
    "Nom du compteur",
    "Identifiant du site de comptage",
    "Nom du site de comptage",
    "Comptage horaire",
    "Date et heure de comptage",
    "Date d'installation du site de comptage",
    "Coordonnées géographiques",
]

RENAME_COLUMNS = {
    "Identifiant du compteur": "meter_id",
    "Nom du compteur": "meter_name",
    "Identifiant du site de comptage": "meter_site_identifier",
    "Nom du site de comptage": "meter_site_name",
    "Comptage horaire": "hourly_countings",
    "Date et heure de comptage": "date_time_counting",
    "Date d'installation du site de comptage": "site_installation_date",
    "Coordonnées géographiques": "geo_coordinates",
}

CONDITIONS = {
    "overcast": "clear",
    "clear sky": "clear",
    "partly cloudy": "clear",
    "mainly clear": "clear",
    "light drizzle": "light rain",
    "slight rain": "light rain",
    "moderate drizzle": "heavy rain",
    "dense (heavy) drizzle": "heavy rain",
    "moderate rain": "heavy rain",
    "heavy rain": "heavy rain",
    "slight snow fall": "snowfall",
    "moderate snow fall": "snowfall",
    "heavy snow fall": "snowfall",
}


def build_weather(start_date: str, end_date: str) -> pd.DataFrame:
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 48.8534,
        "longitude": 2.3488,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,weather_code,precipitation",
        "timezone": "Europe/Berlin",
    }
    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()
    hourly = response.json()["hourly"]
    weather_time = pd.Series(pd.to_datetime(hourly["time"]))
    weather = pd.DataFrame(
        {
            "weather_date": weather_time.dt.tz_localize(
                "Europe/Berlin", nonexistent="shift_forward", ambiguous=True
            ).dt.tz_convert("UTC"),
            "temperature": hourly["temperature_2m"],
            "precipitation": hourly["precipitation"],
            "weather_code": hourly["weather_code"],
        }
    )
    weather["weather_code"] = weather["weather_code"].astype("int64")

    wmo = pd.read_csv(WMO_PATH)
    weather = weather.merge(wmo, left_on="weather_code", right_on="code", how="left")
    weather = weather.drop(columns=["code"])
    weather["weather_conditions"] = weather["code_description"].map(CONDITIONS)
    weather["weather_conditions"] = weather["weather_conditions"].fillna("other")
    weather = weather.drop_duplicates("weather_date", keep="first")
    return weather


def main() -> None:
    print(f"Reading raw counter data from {RAW_PATH}")
    traffic = pd.read_csv(RAW_PATH, sep=";", usecols=RAW_COLUMNS, encoding="utf-8-sig")
    traffic = traffic.rename(columns=RENAME_COLUMNS)

    duplicate_meter = "147 avenue d'Italie 147 avenue d'Italie [Bike]"
    traffic = traffic[traffic["meter_name"] != duplicate_meter].reset_index(drop=True)
    print(f"Rows after duplicate meter removal: {len(traffic):,}")

    traffic["site_installation_date"] = pd.to_datetime(
        traffic["site_installation_date"], utc=True
    )
    traffic[["latitude", "longitude"]] = (
        traffic["geo_coordinates"].str.split(",", expand=True).astype(float)
    )
    traffic = traffic.drop(columns=["geo_coordinates"])

    traffic["date_time_counting"] = pd.to_datetime(
        traffic["date_time_counting"], errors="coerce", utc=True
    )
    traffic["date"] = traffic["date_time_counting"].dt.tz_convert(None).dt.normalize()
    traffic["hour"] = traffic["date_time_counting"].dt.hour.astype("int32")
    traffic["weekday"] = traffic["date_time_counting"].dt.day_name()
    traffic["is_weekend"] = traffic["date_time_counting"].dt.weekday >= 5
    traffic["month"] = traffic["date_time_counting"].dt.month.astype("int32")
    traffic["year"] = traffic["date_time_counting"].dt.year.astype("int32")
    traffic["week"] = traffic["date_time_counting"].dt.isocalendar().week

    print("Computing KMeans area groups")
    coords = traffic[["latitude", "longitude"]].dropna().copy()
    kmeans = KMeans(n_clusters=6, n_init=30, random_state=42)
    coords["area"] = kmeans.fit_predict(coords) + 1
    traffic.loc[coords.index, "area"] = coords["area"]
    traffic["area"] = traffic["area"].astype("Int64")

    print("Merging school holidays")
    holidays = pd.read_csv(HOLIDAYS_PATH)
    holidays = holidays.rename(
        columns={"is_school_holiday_paris_zone_c": "is_school_holiday"}
    )
    holidays["date"] = pd.to_datetime(holidays["date"])
    traffic = traffic.merge(holidays, on="date", how="left")
    traffic["is_school_holiday"] = traffic["is_school_holiday"].fillna(False).astype(bool)

    start_date = traffic["date"].min().strftime("%Y-%m-%d")
    end_date = traffic["date"].max().strftime("%Y-%m-%d")
    print(f"Fetching weather from Open-Meteo for {start_date} to {end_date}")
    weather = build_weather(start_date, end_date)
    traffic = traffic.merge(
        weather,
        left_on="date_time_counting",
        right_on="weather_date",
        how="left",
    ).drop(columns=["weather_date"])

    print("Merging arrondissement lookup")
    lookup = pd.read_csv(LOOKUP_PATH)
    traffic = traffic.merge(
        lookup,
        left_on="meter_name",
        right_on="Name of Meter",
        how="left",
    ).drop(columns=["Name of Meter"])

    missing_arr = traffic["arrondissement"].isna().sum()
    if missing_arr:
        raise ValueError(f"{missing_arr:,} rows are missing arrondissement values")
    traffic["arrondissement"] = traffic["arrondissement"].astype("int64")

    ordered_columns = [
        "meter_id",
        "meter_name",
        "meter_site_identifier",
        "meter_site_name",
        "hourly_countings",
        "date_time_counting",
        "site_installation_date",
        "latitude",
        "longitude",
        "date",
        "hour",
        "weekday",
        "is_weekend",
        "month",
        "year",
        "week",
        "area",
        "is_school_holiday",
        "temperature",
        "precipitation",
        "weather_code",
        "code_description",
        "weather_conditions",
        "arrondissement",
    ]
    traffic = traffic[ordered_columns]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing {len(traffic):,} rows to {OUTPUT_PATH}")
    traffic.to_csv(OUTPUT_PATH, index=False)
    print("Done")
    print("Arrondissements:", sorted(traffic["arrondissement"].unique().tolist()))


if __name__ == "__main__":
    main()
