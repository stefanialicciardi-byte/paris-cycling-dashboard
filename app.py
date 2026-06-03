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
ARRONDISSEMENT_CENTROIDS = {
    1: (48.8626, 2.3363),
    2: (48.8680, 2.3426),
    3: (48.8637, 2.3615),
    4: (48.8543, 2.3570),
    5: (48.8448, 2.3500),
    6: (48.8493, 2.3320),
    7: (48.8565, 2.3126),
    8: (48.8770, 2.3170),
    9: (48.8772, 2.3375),
    10: (48.8760, 2.3600),
    11: (48.8585, 2.3790),
    12: (48.8408, 2.3880),
    13: (48.8322, 2.3561),
    14: (48.8331, 2.3264),
    15: (48.8422, 2.2928),
    16: (48.8637, 2.2769),
    17: (48.8872, 2.3060),
    18: (48.8925, 2.3444),
    19: (48.8870, 2.3840),
    20: (48.8630, 2.3980),
}


def inject_app_style() -> None:
    st.markdown(
        """
        <style>
            .section-copy {
                color: #374151;
                font-size: 1.02rem;
                line-height: 1.65;
            }
            .objective-box {
                margin-top: 2rem;
                padding: 1.1rem 1.35rem;
                border-left: 5px solid #2563eb;
                background: #eef4ff;
                border-radius: 6px;
            }
            .objective-box strong {
                display: block;
                margin-bottom: 0.35rem;
            }
            .takeaway-box {
                margin: 1.1rem 0 0.5rem 0;
                padding: 1rem 1.15rem;
                border-left: 5px solid #0f766e;
                background: #ecfdf5;
                border-radius: 6px;
                color: #134e4a;
            }
            .date-range-box {
                margin-top: 1.35rem;
                padding: 0.95rem 1.1rem;
                border: 1px solid #dbe4f0;
                border-radius: 6px;
                background: #f8fafc;
            }
            .date-range-label {
                color: #4b5563;
                font-size: 0.9rem;
                font-weight: 700;
            }
            .date-range-value {
                margin-top: 0.2rem;
                color: #111827;
                font-size: 1.35rem;
                font-weight: 650;
            }
            section[data-testid="stSidebar"] {
                background: #f3f5f9;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] > div {
                gap: 0.65rem;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] label {
                min-height: 2.55rem;
                margin: 0;
                padding: 0.45rem 0.95rem;
                border-radius: 0.55rem;
                color: #4b5563;
                font-size: 1.04rem;
                font-weight: 500;
                transition: background 120ms ease, color 120ms ease;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
                background: #e8edf6;
                color: #111827;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
                background: #dbe2ee;
                color: #111827;
                font-weight: 750;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
                display: none;
            }
            section[data-testid="stSidebar"] [data-testid="stRadio"] p {
                font-size: 1.04rem;
                line-height: 1.35;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
    count_cols = ["n_rows", "n_meters", "total_hourly"]
    summary[count_cols] = summary[count_cols].astype(int)
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
    summary["arrondissement_full"] = summary["arrondissement"].apply(
        lambda value: (
            "Paris 1er arrondissement"
            if value == 1
            else f"Paris {int(value)}e arrondissement"
        )
    )
    summary["latitude"] = summary["arrondissement"].map(
        lambda value: ARRONDISSEMENT_CENTROIDS[int(value)][0]
    )
    summary["longitude"] = summary["arrondissement"].map(
        lambda value: ARRONDISSEMENT_CENTROIDS[int(value)][1]
    )
    summary["coverage_status"] = "Over-covered"
    summary.loc[summary["meters_vs_hourly_gap_pct"] < -1, "coverage_status"] = (
        "Under-covered"
    )
    summary.loc[summary["meters_vs_hourly_gap_pct"].abs() <= 1, "coverage_status"] = (
        "Balanced"
    )
    summary["marker_size"] = summary["n_meters"].clip(lower=1)
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

    st.title("Cycling Through Paris")
    st.caption("Tracking Paris cycling flows through counters, weather, and time.")
    st.divider()

    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Project Context")
        st.markdown(
            """
            <p class="section-copy">
            Cycling has become a central part of Paris mobility, but the pattern
            is not uniform across the city. Traffic rises and falls with commuting
            hours, school calendars, weather conditions, and the placement of
            bicycle counters.
            </p>
            <p class="section-copy">
            This project uses public bicycle counter data enriched with contextual
            variables to explore when cycling demand is strongest and whether
            counter coverage reflects that demand across arrondissements.
            </p>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if HERO_IMAGE_PATH.exists():
            st.image(HERO_IMAGE_PATH, width="stretch")
            st.caption("Generated editorial image for the dashboard introduction.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total bicycle countings", f"{total_countings:,.0f}")
    c2.metric("Counter locations", f"{counter_count:,.0f}")
    c3.metric("Observation window", f"{start_date} - {end_date}")

    st.markdown(
        f"""
        <div class="objective-box">
            <strong>Project Objective</strong>
            Build an interactive analytical foundation for understanding Paris bicycle
            traffic across time, weather, holidays, and arrondissement coverage using
            {counter_count:,} counter locations and {total_countings:,.0f} recorded countings.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.button(
        "Explore the interactive dashboard",
        type="primary",
        on_click=go_to_interactive_dashboard,
    )


def go_to_interactive_dashboard() -> None:
    st.session_state["page"] = "Interactive Dashboard"


def show_page_title(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def show_takeaway(text: str) -> None:
    st.markdown(
        f"""
        <div class="takeaway-box">
            <strong>Takeaway</strong><br>{text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_data_sources_page(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    show_page_title(
        "Data Sources",
        "The dashboard is built from an enriched Paris cycling traffic dataset exported from the notebook.",
    )
    source_rows = int(df["counter_locations"].sum())
    st.markdown(
        """
        The original notebook created `traffic_enriched.csv`, combining bicycle
        counter readings with calendar fields, school-holiday flags, weather
        variables, and arrondissement labels. For deployment, the app uses a
        lighter aggregated extract while preserving the same analytical fields.
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Original Rows", f"{source_rows:,}")
    c2.metric("Dashboard Records", f"{len(df):,}")
    c3.metric("Columns", f"{len(df.columns):,}")
    c4.metric("Weather Classes", f"{df['weather_condition'].nunique():,}")

    start_date = df["date"].min().strftime("%B %-d, %Y")
    end_date = df["date"].max().strftime("%B %-d, %Y")
    st.markdown(
        f"""
        <div class="date-range-box">
            <div class="date-range-label">Date range</div>
            <div class="date-range-value">{start_date} - {end_date}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Preview of the dashboard extract")
    preview_cols = [
        "date",
        "hour",
        "weekday",
        "arrondissement",
        "hourly_countings",
        "temperature",
        "precipitation",
        "weather_condition",
        "school_holiday",
        "counter_locations",
    ]
    st.dataframe(df[preview_cols].head(), hide_index=True, width="stretch")

    show_takeaway(
        "The Streamlit app reads the deployment-safe CSV, but the counts represent the enriched counter-hour records produced in the notebook."
    )


def show_data_preparation_page(df: pd.DataFrame) -> None:
    show_page_title(
        "Data Preparation",
        "A compact ETL workflow turns raw counter records into analysis-ready dashboard data.",
    )
    st.markdown(
        """
        1. Standardized date, hour, weekday, holiday, and weather fields.
        2. Normalized weather labels into dashboard-friendly categories.
        3. Added weekend and school-holiday indicators for behavioral comparisons.
        4. Aggregated arrondissement-level meter, area, and traffic shares.
        5. Created coverage-status labels to compare counter placement with observed demand.
        """
    )

    sample_cols = [
        "date",
        "hour",
        "weekday",
        "arrondissement",
        "hourly_countings",
        "temperature",
        "precipitation",
        "weather_condition",
        "school_holiday",
        "coverage_status",
    ]
    st.subheader("Analysis-Ready Sample")
    st.dataframe(df[sample_cols].head(12), hide_index=True, width="stretch")
    show_takeaway(
        "The preparation step makes the dashboard more than a chart collection: each visual can compare time, place, weather, and coverage with consistent fields."
    )


def show_cycling_patterns_page(df: pd.DataFrame) -> None:
    show_page_title(
        "Cycling Patterns",
        "Daily and weekly rhythms reveal how strongly cycling traffic reflects commuting behavior.",
    )
    left, right = st.columns(2)
    with left:
        plot_hourly_patterns(df, "story_patterns")
    with right:
        plot_calendar_patterns(df, "story_patterns")
    show_takeaway(
        "The strongest signals are temporal: average traffic rises around commute periods and weekdays behave differently from weekends."
    )


def show_weather_impact_page(df: pd.DataFrame) -> None:
    show_page_title(
        "Weather Impact",
        "Weather adds useful context for interpreting lower-volume days and seasonal differences.",
    )
    left, right = st.columns(2)
    with left:
        plot_weather(df, "story_weather")
    with right:
        corr = df[["hourly_countings", "temperature", "precipitation"]].corr()
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
    show_takeaway(
        "Rain and snowfall are associated with lower bicycle counts, while temperature provides additional context for daily variation."
    )


def show_conclusion_page() -> None:
    show_page_title(
        "Conclusion",
        "The project shows how cycling demand changes by time, conditions, and place.",
    )
    st.markdown(
        """
        **Main findings**

        - Cycling traffic has clear morning and evening commuting peaks.
        - Weekday traffic is stronger than weekend traffic.
        - School holidays reduce cycling volume, especially during commute periods.
        - Rain and snowfall are linked with lower cycling counts.
        - Counter meters are not evenly distributed across Paris.
        - Some busy central areas appear under-covered because their traffic share is higher than their meter share.
        - The 3e arrondissement is strongly under-covered, while the 12e arrondissement is over-covered relative to cycling demand.

        **Future improvements**

        - Add bicycle-lane infrastructure data.
        - Compare demand with population, employment, or land-use density.
        - Include longer seasonal history.
        - Add predictive modeling for expected traffic under different weather conditions.
        """
    )
    show_takeaway(
        "New counter placement should prioritize arrondissements where cycling activity is intense but meter coverage is relatively low."
    )


def show_kpis(summary: pd.DataFrame) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cycling Count", f"{summary['total_hourly'].sum():,.0f}")
    col2.metric("Counter Meters", f"{summary['n_meters'].sum():,.0f}")
    col3.metric("Paris Arrondissements", f"{len(ARRONDISSEMENT_AREA_KM2)}")


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


def plot_map(summary: pd.DataFrame) -> None:
    map_data = summary.copy()
    fig_outline = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        size="marker_size",
        color_discrete_sequence=["#111827"],
        size_max=46,
        hover_name="arrondissement_full",
        hover_data={
            "n_meters": ":,",
            "total_hourly": ":,.0f",
            "area_share_pct": ":.1f",
            "meters_share_pct": ":.1f",
            "hourly_share_pct": ":.1f",
            "meters_vs_hourly_gap_pct": ":.1f",
            "marker_size": False,
            "latitude": False,
            "longitude": False,
        },
        zoom=11,
        height=620,
        title="Paris Cycling Counter Coverage by Arrondissement",
    )
    for trace in fig_outline.data:
        trace.update(showlegend=False, hoverinfo="skip", marker={"opacity": 0.75})

    fig_points = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        size="marker_size",
        color="coverage_status",
        color_discrete_map={
            "Under-covered": "#EF4444",
            "Balanced": "#2563EB",
            "Over-covered": "#16A34A",
        },
        hover_name="arrondissement_full",
        hover_data={
            "n_meters": ":,",
            "total_hourly": ":,.0f",
            "area_share_pct": ":.1f",
            "meters_share_pct": ":.1f",
            "hourly_share_pct": ":.1f",
            "meters_vs_hourly_gap_pct": ":.1f",
            "marker_size": False,
            "latitude": False,
            "longitude": False,
        },
        size_max=34,
        zoom=11,
        height=620,
        title="Paris Cycling Counter Coverage by Arrondissement",
    )
    fig_map = fig_outline
    fig_map.add_traces(fig_points.data)
    fig_map.update_layout(
        map_style="open-street-map",
        legend_title="Coverage status",
        margin={"r": 0, "t": 45, "l": 0, "b": 0},
    )
    st.plotly_chart(fig_map, width="stretch")


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
inject_app_style()

page_options = [
    "Introduction",
    "Data Sources",
    "Data Preparation",
    "Cycling Patterns",
    "Weather Impact",
    "Interactive Dashboard",
    "Conclusion",
]
if st.session_state.get("page") not in page_options:
    st.session_state["page"] = "Introduction"

with st.sidebar:
    page = st.radio(
        "Page",
        page_options,
        key="page",
        label_visibility="collapsed",
    )

if page == "Introduction":
    show_intro_page(traffic, summary)
elif page == "Data Sources":
    show_data_sources_page(traffic, summary)
elif page == "Data Preparation":
    show_data_preparation_page(traffic)
elif page == "Cycling Patterns":
    show_cycling_patterns_page(traffic)
elif page == "Weather Impact":
    show_weather_impact_page(traffic)
elif page == "Conclusion":
    show_conclusion_page()
else:
    filtered = filter_traffic(traffic)

    st.title("Paris Cycling Traffic Dashboard")
    st.caption(
        "Tracking Paris cycling flows through counters, weather, and time."
    )

    if filtered.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    show_kpis(summary)

    overview_tab, traffic_tab, weather_tab, map_tab = st.tabs(
        [
            "Overview",
            "Traffic Patterns",
            "Weather & Holidays",
            "Map",
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
                - The map highlights where cycling counter activity is concentrated.
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
        st.markdown(
            """
            This map summarizes counter coverage by arrondissement. Marker size
            represents the number of counter meters, while color compares each
            arrondissement's meter share with its cycling-traffic share:
            **red** is under-covered, **blue** is balanced, and **green** is over-covered.
            A negative gap means there are too few meters for the observed cycling
            demand; a positive gap means there are more meters than traffic share suggests.
            """
        )
        plot_map(summary)

st.caption(
    "Project by Sascha Behrens, Victoria Ford, and Stefania Licciardi - Data Analytics Bootcamp"
)
