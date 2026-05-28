from base64 import b64encode
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Paris Cycling Traffic Dashboard",
    page_icon=":bike:",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
TRAFFIC_PATH = BASE_DIR / "data" / "streamlit_public_traffic.csv"
FULL_TRAFFIC_PATH = BASE_DIR / "data" / "traffic_enriched.csv"
SAMPLE_TRAFFIC_PATH = BASE_DIR / "data" / "cycling_clean_sample.csv"
SUMMARY_PATH = BASE_DIR / "data" / "cycling_traffic_summary.csv"
HERO_IMAGE_PATH = BASE_DIR / "assets" / "paris-cycling-hero.jpg"
WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
WEATHER_ORDER = ["clear", "light rain", "heavy rain", "snowfall"]
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


def image_as_data_uri(path: Path) -> str:
    image_bytes = path.read_bytes()
    encoded = b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


@st.cache_data
def load_traffic(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    if "school_holiday" not in df.columns and "is_school_holiday" in df.columns:
        df["school_holiday"] = df["is_school_holiday"]
    if "weather_condition" not in df.columns and "weather_conditions" in df.columns:
        df["weather_condition"] = df["weather_conditions"]

    df["school_holiday"] = df["school_holiday"].astype(bool)
    if "is_weekend" not in df.columns:
        df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"])
    return df


@st.cache_data
def load_summary(path: Path) -> pd.DataFrame:
    summary = pd.read_csv(path)
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
    count_cols = ["n_rows", "n_meters", "total_hourly"]
    summary[count_cols] = summary[count_cols].fillna(0).astype(int)
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
    summary["arrondissement_label"] = (
        summary["arrondissement"].astype(int).astype(str) + "e"
    )
    summary["coverage_status"] = "Over-covered"
    summary.loc[summary["meters_vs_hourly_gap_pct"] < 0, "coverage_status"] = (
        "Under-covered"
    )
    summary.loc[summary["n_rows"] == 0, "coverage_status"] = "No data"
    return summary.sort_values("arrondissement")


def require_files() -> None:
    missing = [
        str(path.relative_to(BASE_DIR))
        for path in [TRAFFIC_PATH, SUMMARY_PATH]
        if not path.exists()
    ]
    if TRAFFIC_PATH.exists():
        return
    if FULL_TRAFFIC_PATH.exists() and SUMMARY_PATH.exists():
        return
    if SAMPLE_TRAFFIC_PATH.exists() and SUMMARY_PATH.exists():
        st.warning(
            "Using the small sample CSV because `data/traffic_enriched.csv` was not found."
        )
        return
    if missing:
        st.error("Missing required file(s): " + ", ".join(missing))
        st.stop()


def filter_traffic(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filters")
        arrondissements = sorted(df["arrondissement"].dropna().unique())
        selected_arrondissements = st.multiselect(
            "Arrondissement",
            arrondissements,
            default=arrondissements,
        )

        weather_conditions = sorted(df["weather_condition"].dropna().unique())
        selected_weather = st.multiselect(
            "Weather condition",
            weather_conditions,
            default=weather_conditions,
        )

        day_type = st.segmented_control(
            "Day type",
            ["All", "Weekdays", "Weekends"],
            default="All",
        )
        holiday_filter = st.radio(
            "School holiday",
            ["All", "Holiday only", "Non-holiday only"],
        )

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        selected_dates = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    filtered = df[
        df["arrondissement"].isin(selected_arrondissements)
        & df["weather_condition"].isin(selected_weather)
    ].copy()

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered = filtered[
            (filtered["date"].dt.date >= start_date)
            & (filtered["date"].dt.date <= end_date)
        ]

    if day_type == "Weekdays":
        filtered = filtered[~filtered["is_weekend"]]
    elif day_type == "Weekends":
        filtered = filtered[filtered["is_weekend"]]

    if holiday_filter == "Holiday only":
        filtered = filtered[filtered["school_holiday"]]
    elif holiday_filter == "Non-holiday only":
        filtered = filtered[~filtered["school_holiday"]]

    return filtered


def show_intro_page(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    total_countings = df["hourly_countings"].sum()
    counter_count = int(summary["n_meters"].sum())
    start_date = df["date"].min().strftime("%b %Y")
    end_date = df["date"].max().strftime("%b %Y")

    hero_background = image_as_data_uri(HERO_IMAGE_PATH) if HERO_IMAGE_PATH.exists() else ""
    st.markdown(
        f"""
        <style>
            .intro-hero {{
                min-height: 430px;
                padding: clamp(2.2rem, 6vw, 5rem);
                display: flex;
                align-items: flex-end;
                border-radius: 0;
                color: #ffffff;
                background:
                    linear-gradient(90deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.34), rgba(15, 23, 42, 0.08)),
                    url("{hero_background}");
                background-size: cover;
                background-position: center;
            }}
            .intro-copy {{
                max-width: 760px;
            }}
            .intro-kicker {{
                margin-bottom: 0.75rem;
                color: #bfdbfe;
                font-size: 0.84rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }}
            .intro-title {{
                margin: 0;
                font-size: clamp(3rem, 6vw, 5.8rem);
                line-height: 0.96;
                font-weight: 800;
                letter-spacing: 0;
            }}
            .intro-subtitle {{
                margin-top: 1.25rem;
                max-width: 620px;
                color: #e5e7eb;
                font-size: clamp(1.05rem, 2vw, 1.35rem);
                line-height: 1.55;
            }}
            .intro-section {{
                padding: 2.3rem 0 0.4rem 0;
            }}
            .intro-section h2 {{
                margin-bottom: 0.8rem;
                font-size: 1.55rem;
            }}
            .intro-section p {{
                color: #4b5563;
                font-size: 1.02rem;
                line-height: 1.65;
            }}
        </style>
        <section class="intro-hero">
            <div class="intro-copy">
                <div class="intro-kicker">Paris bicycle counter analysis</div>
                <h1 class="intro-title">Cycling Through Paris</h1>
                <p class="intro-subtitle">
                    A data story about everyday bicycle movement across the city,
                    from commute peaks to weather-sensitive riding patterns.
                </p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Total bicycle countings", f"{total_countings:,.0f}")
    c2.metric("Counter locations", f"{counter_count:,.0f}")
    c3.metric("Observation window", f"{start_date} - {end_date}")

    st.markdown(
        """
        <section class="intro-section">
            <h2>What This Dashboard Reveals</h2>
            <p>
                Paris cycling activity follows a clear urban rhythm. This project brings
                together counter readings, weather, school holidays, time patterns, and
                arrondissement coverage to show how bicycle traffic changes across the city.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Time")
        st.write("Compare weekday, weekend, hourly, and holiday patterns.")
    with col2:
        st.subheader("Conditions")
        st.write("See how temperature, rain, and snowfall relate to cycling volume.")
    with col3:
        st.subheader("Coverage")
        st.write("Check whether counter placement reflects arrondissement demand.")

    if st.button("Explore the dashboard", type="primary"):
        st.session_state["page"] = "Dashboard"
        st.rerun()


def show_kpis(filtered: pd.DataFrame, summary: pd.DataFrame) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Countings", f"{filtered['hourly_countings'].sum():,.0f}")
    col2.metric("Average Hourly Count", f"{filtered['hourly_countings'].mean():.1f}")
    col3.metric("Counter Locations", f"{filtered[['latitude', 'longitude']].drop_duplicates().shape[0]:,}")
    col4.metric("Average Temperature", f"{filtered['temperature'].mean():.1f} °C")
    col5.metric("Arrondissements", f"{summary['arrondissement'].nunique()}/20")


def plot_hourly_patterns(filtered: pd.DataFrame, key_prefix: str) -> None:
    hourly = (
        filtered.groupby("hour", as_index=False)["hourly_countings"]
        .mean()
        .sort_values("hour")
    )
    fig_hourly = px.line(
        hourly,
        x="hour",
        y="hourly_countings",
        markers=True,
        title="Average Cycling Traffic by Hour of Day",
    )
    fig_hourly.update_layout(
        xaxis_title="Hour of day",
        yaxis_title="Average bicycle countings",
        height=420,
    )
    st.plotly_chart(fig_hourly, width="stretch", key=f"{key_prefix}_hourly")

    hourly_weekend = (
        filtered.groupby(["hour", "is_weekend"], as_index=False)["hourly_countings"]
        .mean()
        .sort_values("hour")
    )
    hourly_weekend["day_type"] = hourly_weekend["is_weekend"].map(
        {False: "Weekday", True: "Weekend"}
    )
    fig_weekend = px.line(
        hourly_weekend,
        x="hour",
        y="hourly_countings",
        color="day_type",
        markers=True,
        title="Weekday vs Weekend Hourly Profile",
    )
    fig_weekend.update_layout(
        xaxis_title="Hour of day",
        yaxis_title="Average bicycle countings",
        height=420,
    )
    st.plotly_chart(fig_weekend, width="stretch", key=f"{key_prefix}_weekend")


def plot_calendar_patterns(filtered: pd.DataFrame, key_prefix: str) -> None:
    weekday_data = (
        filtered.groupby("weekday", as_index=False)["hourly_countings"]
        .mean()
    )
    weekday_data["weekday"] = pd.Categorical(
        weekday_data["weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )
    weekday_data = weekday_data.sort_values("weekday")
    fig_weekday = px.bar(
        weekday_data,
        x="weekday",
        y="hourly_countings",
        title="Day-of-Week Cycling Traffic",
    )
    fig_weekday.update_layout(
        xaxis_title="Day of week",
        yaxis_title="Average hourly bicycle countings",
        height=420,
    )
    st.plotly_chart(fig_weekday, width="stretch", key=f"{key_prefix}_weekday")

    holiday_data = (
        filtered.groupby(["weekday", "school_holiday"], as_index=False)[
            "hourly_countings"
        ]
        .mean()
    )
    holiday_data["weekday"] = pd.Categorical(
        holiday_data["weekday"],
        categories=WEEKDAY_ORDER,
        ordered=True,
    )
    holiday_data = holiday_data.sort_values("weekday")
    fig_holiday = px.bar(
        holiday_data,
        x="weekday",
        y="hourly_countings",
        color="school_holiday",
        barmode="group",
        title="School Holiday Effect by Weekday",
    )
    fig_holiday.update_layout(
        xaxis_title="Day of week",
        yaxis_title="Average hourly bicycle countings",
        height=420,
        legend_title="School holiday",
    )
    st.plotly_chart(fig_holiday, width="stretch", key=f"{key_prefix}_holiday")


def plot_weather(filtered: pd.DataFrame, key_prefix: str) -> None:
    weather_data = (
        filtered.groupby("weather_condition", as_index=False)
        .agg(
            avg_hourly_countings=("hourly_countings", "mean"),
            avg_temperature=("temperature", "mean"),
            avg_precipitation=("precipitation", "mean"),
        )
    )
    weather_data["weather_condition"] = pd.Categorical(
        weather_data["weather_condition"],
        categories=WEATHER_ORDER,
        ordered=True,
    )
    weather_data = weather_data.sort_values("weather_condition")
    fig_weather = px.bar(
        weather_data,
        x="weather_condition",
        y="avg_hourly_countings",
        hover_data={
            "avg_temperature": ":.1f",
            "avg_precipitation": ":.2f",
            "avg_hourly_countings": ":.1f",
        },
        title="Average Hourly Countings per Weather Condition",
    )
    fig_weather.update_layout(
        xaxis_title="Weather condition",
        yaxis_title="Average hourly bicycle countings",
        height=420,
    )
    st.plotly_chart(fig_weather, width="stretch", key=f"{key_prefix}_weather")

    fig_temp = px.scatter(
        filtered,
        x="temperature",
        y="hourly_countings",
        color="school_holiday",
        size="precipitation",
        hover_data=["date", "weekday", "weather_condition", "arrondissement"],
        title="Temperature, Precipitation, and Bicycle Traffic",
    )
    fig_temp.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="Hourly bicycle countings",
        height=420,
        legend_title="School holiday",
    )
    st.plotly_chart(fig_temp, width="stretch", key=f"{key_prefix}_temperature")


def plot_map(filtered: pd.DataFrame) -> None:
    map_data = (
        filtered.groupby(
            ["arrondissement", "latitude", "longitude", "coverage_status"],
            as_index=False,
        )
        .agg(
            avg_hourly_countings=("hourly_countings", "mean"),
            total_hourly_countings=("hourly_countings", "sum"),
        )
    )
    fig_map = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        size="avg_hourly_countings",
        color="coverage_status",
        hover_name="arrondissement",
        hover_data={
            "avg_hourly_countings": ":.1f",
            "total_hourly_countings": ":,.0f",
            "latitude": False,
            "longitude": False,
        },
        zoom=11,
        height=620,
        title="Cycling Counters by Coverage Status",
    )
    fig_map.update_layout(
        map_style="open-street-map",
        margin={"r": 0, "t": 45, "l": 0, "b": 0},
    )
    st.plotly_chart(fig_map, width="stretch")


def plot_coverage(summary: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    with col1:
        coverage = summary.sort_values("arrondissement")
        fig_gap = px.bar(
            coverage,
            x="arrondissement_label",
            y="meters_vs_hourly_gap_pct",
            color="coverage_status",
            title="Meter Coverage Gap vs Cycling Demand",
        )
        fig_gap.update_layout(
            xaxis_title="Arrondissement",
            yaxis_title="Meters share - traffic share (pp)",
            height=430,
        )
        st.plotly_chart(fig_gap, width="stretch")

    with col2:
        mix = summary.melt(
            id_vars=["arrondissement_label"],
            value_vars=["area_share_pct", "meters_share_pct", "hourly_share_pct"],
            var_name="metric",
            value_name="share_pct",
        )
        mix["metric"] = mix["metric"].map(
            {
                "area_share_pct": "Area share",
                "meters_share_pct": "Meter share",
                "hourly_share_pct": "Traffic share",
            }
        )
        fig_mix = px.bar(
            mix,
            x="arrondissement_label",
            y="share_pct",
            color="metric",
            barmode="group",
            title="Area, Meter, and Traffic Share by Arrondissement",
        )
        fig_mix.update_layout(
            xaxis_title="Arrondissement",
            yaxis_title="Share of Paris total (%)",
            height=430,
            legend_title="Metric",
        )
        st.plotly_chart(fig_mix, width="stretch")

    st.dataframe(
        summary[
            [
                "arrondissement",
                "n_meters",
                "total_hourly",
                "area_share_pct",
                "meters_share_pct",
                "hourly_share_pct",
                "meter_vs_area_gap_pct",
                "meters_vs_hourly_gap_pct",
                "coverage_status",
            ]
        ].sort_values("arrondissement"),
        width="stretch",
        hide_index=True,
    )


require_files()
if TRAFFIC_PATH.exists():
    active_traffic_path = TRAFFIC_PATH
elif FULL_TRAFFIC_PATH.exists():
    active_traffic_path = FULL_TRAFFIC_PATH
else:
    active_traffic_path = SAMPLE_TRAFFIC_PATH
traffic = load_traffic(active_traffic_path)
summary = load_summary(SUMMARY_PATH)
if "coverage_status" not in traffic.columns:
    traffic = traffic.merge(
        summary[["arrondissement", "coverage_status"]],
        on="arrondissement",
        how="left",
    )

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Page",
        ["Introduction", "Dashboard"],
        key="page",
        label_visibility="collapsed",
    )

if page == "Introduction":
    show_intro_page(traffic, summary)
    st.caption(
        "Project by Sascha Behrens, Victoria Ford, and Stefania Licciardi - Data Analytics Bootcamp"
    )
    st.stop()

filtered = filter_traffic(traffic)

st.title("Paris Cycling Traffic Dashboard")
st.caption(
    "Tracking Paris cycling flows through counters, weather, and time."
)

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

show_kpis(filtered, summary)

overview_tab, traffic_tab, weather_tab, map_tab, coverage_tab, data_tab = st.tabs(
    [
        "Overview",
        "Traffic Patterns",
        "Weather & Holidays",
        "Map",
        "Coverage",
        "Data",
    ]
)

with overview_tab:
    st.subheader("Project Summary")
    st.markdown(
        """
        The project analyzes Paris bicycle counter data enriched with calendar,
        school holiday, weather, and arrondissement coverage context. The core
        question is where and when cycling traffic is strongest, and whether
        counter coverage reflects actual cycling demand.
        """
    )
    c1, c2 = st.columns(2)
    with c1:
        plot_hourly_patterns(filtered, "overview")
    with c2:
        st.markdown(
            """
            **Key findings from the notebook**

            - Cycling traffic has clear morning and evening commuting peaks.
            - Weekday traffic is stronger than weekend traffic.
            - School holidays reduce cycling volume, especially during commute periods.
            - Rain and snowfall are associated with lower cycling counts.
            - Some central arrondissements have high traffic but relatively low meter coverage.
            """
        )

with traffic_tab:
    left, right = st.columns(2)
    with left:
        plot_hourly_patterns(filtered, "traffic")
    with right:
        plot_calendar_patterns(filtered, "traffic")

with weather_tab:
    left, right = st.columns(2)
    with left:
        plot_weather(filtered, "weather")
    with right:
        corr = filtered[["hourly_countings", "temperature", "precipitation"]].corr()
        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Correlation Heatmap",
        )
        fig_corr.update_layout(height=420)
        st.plotly_chart(fig_corr, width="stretch")

with map_tab:
    plot_map(filtered)

with coverage_tab:
    plot_coverage(summary)

with data_tab:
    st.subheader("Filtered Traffic Data")
    st.dataframe(filtered, width="stretch", hide_index=True)
    st.subheader("Arrondissement Coverage Summary")
    st.dataframe(summary, width="stretch", hide_index=True)

st.caption(
    "Project by Sascha Behrens, Victoria Ford, and Stefania Licciardi - Data Analytics Bootcamp"
)
