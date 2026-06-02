import streamlit as st
from datetime import date, timedelta
from weather_router import run_many
import re
import pandas as pd
import numpy as np
from io import BytesIO
import zipfile
import config
from datetime import time




default_launch_latitude = 47.965378
default_launch_longitude = -81.873536

st.title("Meteo Data to CSV")


unit_label = st.selectbox(
    "Wind speed unit",
    options=["Default (km/h)", "kn", "ms", "mph"],
    index=0,
)


agree = st.checkbox("Do you agree to the terms?")

if agree:
    st.write("Great! Proceeding to the next step.")


wind_speed_unit = "" if unit_label == "Default (km/h)" else unit_label


DAILY_VARS = ["wind_gusts_10m_mean"]

EXTRA_PARAMS = {"models": "best_match",}
if wind_speed_unit:
    EXTRA_PARAMS["wind_speed_unit"] = wind_speed_unit



def sanitize_filename(name: str) -> str:
    """
    Keep filenames safe across OS:
    letters, numbers, dash, underscore only.
    """
    name = name.strip()
    name = re.sub(r"[^A-Za-z0-9_\-]+", "_", name)
    return name or "meteo"


def ensure_sorted_hourly(df: pd.DataFrame):
    tcol = "time" if "time" in df.columns else ("date" if "date" in df.columns else None)
    # df[tcol] = df[tcol].dt.strftime("%Y-%m-%d %H:%M")
    # df[tcol] = pd.to_datetime(df[tcol])
    # df[tcol] = df[tcol].dt.strftime("%Y-%m-%d %H:%M")
    if tcol is None:
        raise KeyError(f"Hourly df missing time column. Columns: {list(df.columns)}")

    out = df.copy()
    out[tcol] = pd.to_datetime(out[tcol], utc=True, errors="coerce")
    out = out.dropna(subset=[tcol]).sort_values(tcol).reset_index(drop=True)
    return out, tcol


def make_filtered_sorted(df_hourly: pd.DataFrame) -> pd.DataFrame:
    """
    Filters:
      - day only (is_day == 1)
      - between 8am and before 7pm (08:00 <= hour < 19:00)
      - cloud_cover_low < 50
    And returns sorted output.
    """

    df, tcol = ensure_sorted_hourly(df_hourly)

    required = ["is_day", "cloud_cover_low", tcol]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise KeyError(
            f"Missing required columns for filtering: {missing}. "
            f"Have: {list(df.columns)}"
        )

    df = df[
        (df["is_day"] == 1) &
        (df["cloud_cover_low"] < 50) &
        (df[tcol].dt.hour >= 8) &
        (df[tcol].dt.hour <= 19)
    ]

    return df.reset_index(drop=True)



# ----------------------------
# Coords UI
# ----------------------------
def coords():
    if "latitude" not in st.session_state:
        st.session_state.latitude = default_launch_latitude
    if "longitude" not in st.session_state:
        st.session_state.longitude = default_launch_longitude

    if st.button("Reset Coords"):
        st.session_state.latitude = default_launch_latitude
        st.session_state.longitude = default_launch_longitude
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Latitude", -90.0, 90.0, key="latitude", format="%.6f")
    with col2:
        st.number_input("Longitude", -180.0, 180.0, key="longitude", format="%.6f")


# ----------------------------
# Date routing logic
# ----------------------------
def decide_open_meteo_endpoint(
    start_date: date,
    end_date: date,
    today: date,
    historical_days: int = 90,
    forecast_horizon_days: int = 16,
):
    if end_date < start_date:
        return {"ok": False, "error": "End date must be on/after start date.", "mode": None, "ranges": []}

    cutoff = today - timedelta(days=historical_days)
    forecast_max = today + timedelta(days=forecast_horizon_days)

    if end_date > forecast_max:
        return {"ok": False, "error": f"End date cannot be more than {forecast_horizon_days} days in the future.", "mode": None, "ranges": []}

    # Entirely historical
    if end_date < cutoff:
        return {"ok": True, "error": None, "mode": "historical", "ranges": [("historical", start_date, end_date)]}

    # Entirely forecast
    if start_date >= cutoff:
        return {"ok": True, "error": None, "mode": "forecast", "ranges": [("forecast", start_date, end_date)]}

    # Split
    hist_end = cutoff - timedelta(days=1)
    fcst_start = cutoff
    ranges = []
    if start_date <= hist_end:
        ranges.append(("historical", start_date, hist_end))
    if fcst_start <= end_date:
        ranges.append(("forecast", fcst_start, end_date))

    return {"ok": True, "error": None, "mode": "split", "ranges": ranges}


def format_query(item: dict) -> str:
    mode = item.get("mode", "unknown")
    ranges = item.get("ranges", [])
    parts = [f"{kind}: {s.isoformat()} → {e.isoformat()}" for kind, s, e in ranges]
    return parts


# ----------------------------
# Date input + Save/Remove UI
# ----------------------------
def date_ui(today: date):
    if "saved_queries" not in st.session_state:
        st.session_state.saved_queries = []

    # st.subheader("Date range")

    picked = st.date_input("Select date range", value=(), key="date_range")

    # Normalize picked -> (start, end)
    start_date, end_date = (None, None)
    if isinstance(picked, tuple) and len(picked) == 2:
        start_date, end_date = picked
    elif not isinstance(picked, tuple):
        start_date, end_date = picked, None  # single date picked

    st.session_state.current_decision = None

    if start_date and end_date:
        decision = decide_open_meteo_endpoint(start_date, end_date, today=today)
        if decision["ok"]:
            st.session_state.current_decision = decision
            # st.caption(f"Will use: **{decision['mode']}**")
        else:
            st.error(decision["error"])

    colA, colB = st.columns([0.25, 1.5])
    with colA:
        if st.button("Add Date", disabled=(st.session_state.current_decision is None)):
            decision = dict(st.session_state.current_decision)  # copy
            decision["label"] = f""             # default name per query
            st.session_state.saved_queries.append(decision)
            st.rerun()

    with colB:
        if st.button("Clear all", disabled=(len(st.session_state.saved_queries) == 0)):
            st.session_state.saved_queries = []
            st.rerun()

    


    




    if st.session_state.saved_queries:
        st.subheader("Saved date queries")
        for i, item in enumerate(st.session_state.saved_queries):
            left, mid, right = st.columns([0.55, 0.30, 0.15])

            with left:
                st.write(f"{i+1}. {format_query(item)}")

            with mid:
                # per-query filename label
                key = f"label_{i}"
                default_val = item.get("label", f"query_{i+1:02d}")
                new_label = st.text_input("File name", value=default_val, key=key)
                item["label"] = sanitize_filename(new_label)  # keep it safe

            with right:
                if st.button("Remove", key=f"rm_{i}"):
                    st.session_state.saved_queries.pop(i)
                    st.rerun()



# ----------------------------
# Run app
# ----------------------------
today = date.today()
coords()
date_ui(today)

st.divider()



st.subheader("Export settings")
base_name_raw = st.text_input("Output zipfile name", value="")
base_name = sanitize_filename(base_name_raw)




if st.button("Fetch weather"):
    saved = st.session_state.get("saved_queries", [])
    if not saved:
        st.warning("Add at least one date query first.")
        st.stop()

    lat = st.session_state.latitude
    lon = st.session_state.longitude

    with st.spinner("Fetching data..."):
        try:
            res = run_many(
                lat,
                lon,
                saved,
                hourly_vars=config.HOURLY_VARS,
                daily_vars=DAILY_VARS,
                extra_params=EXTRA_PARAMS,
            )

            # print("res is this: \n", res)
            # print("this is res type \n", type(res))
        except Exception as e:
            st.error(f"Open-Meteo request failed: {e}")
            st.stop()

    if "hourly" not in res or res["hourly"] is None or len(res["hourly"]) == 0:
        st.info("No hourly data returned.")
        st.stop()

    hourly_all = res["hourly"].copy()

    print("THIS IS hourly_all\n ", hourly_all)
    print("THIS IS TYPE OF hourly_all\n ", type(hourly_all))
    # print(len(hourly_all))

    if "query_id" not in hourly_all.columns:
        st.error("Expected 'query_id' column in hourly output. Check weather_router.run_many().")
        st.stop()

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for qid, decision in enumerate(saved, start=1):
            label = sanitize_filename(decision.get("label", f"query_{qid:02d}"))

            df_q = hourly_all[hourly_all["query_id"] == qid].copy()
            df_q, tcol = ensure_sorted_hourly(df_q)
           
            
            # FULL
            
            # print("tcol is: ", tcol, df_q.columns)
            # print("type of date column is: ", df_q[tcol].dtype)
            df_q = df_q.rename(columns={tcol: 'date'})
            # print("tcol after renaming is: ", tcol, df_q.columns)


            df_q["date"] = df_q["date"]
            raw_filtered = df_q.copy()
            # print(raw_filtered["time"])

            

            # FILTERED
            raw_filtered = make_filtered_sorted(raw_filtered)


            time_key = ""
            if "time" in raw_filtered.columns:
                time_key = "time"
            elif "date" in raw_filtered.columns:
                time_key = "date"


            print("this is df_Q")
            print(df_q.head(10))
            print("this is raw_filtered")
            print(raw_filtered.head(10))
            
            df_q["date"] = df_q["date"].dt.strftime("%Y-%m-%d %H:%M")
            raw_filtered["date"] = raw_filtered["date"].dt.strftime("%Y-%m-%d %H:%M")

            


            zf.writestr(
                f"{label}_full-data.csv",
                df_q.to_csv(index=False)
            )

            del raw_filtered["query_id"]
            del raw_filtered["source"]
            del raw_filtered["is_day"]

            zf.writestr(
                f"{label}_filtered-data.csv",
                raw_filtered.to_csv(index=False)
            )


            # SIM_PARAMETER_FULL_DATA

            last_sim_parameters = None
            last_sim_parameters_filtered = None
            hourly_vars = config.HOURLY_VARS
            altitudes = config.ALTITUDES
            wind_speeds = config.WIND_SPEEDS
            wind_directions = config.WIND_DIRECTIONS

            df_q2 = pd.DataFrame()

            time_key = ""
            if "time" in df_q.columns:
                time_key = "time"
            elif "date" in df_q.columns:
                time_key = "date"

            df_q2["date"] = df_q[time_key]#.dt.strftime("%Y-%m-%d %H:%M")
            df_q2["temperature"] = df_q[hourly_vars[hourly_vars.index("temperature_2m")]]
            df_q2["pressure"] = df_q[hourly_vars[hourly_vars.index("pressure_msl")]]

            
            csv_size = len(df_q[time_key])

            for altitude, wind_speed, wind_direction in zip(altitudes, wind_speeds, wind_directions):
                df_q2[f"{altitude}"] = df_q[wind_speed]
                df_q2[f"stdev [{altitude}]"] = np.zeros(csv_size)
                df_q2[f"direction [{altitude}]"] = df_q[wind_direction]
            
            df_q2["cloud_cover_low"] = df_q["cloud_cover_low"]
            df_q2["is_day"] = df_q["is_day"]


            zf.writestr(
                f"sim_parameters_{label}_full-data.csv",
                df_q2.to_csv(index=False)
            )




            # SIM_PARAMETER_FILTERED_DATA


            sim_filtered = make_filtered_sorted(df_q2)

            del sim_filtered["cloud_cover_low"]
            del sim_filtered["is_day"]
            

            zf.writestr(
                f"sim_parameters_{label}_filtered-data.csv",
                sim_filtered.to_csv(index=False)
            )


            last_sim_parameters = df_q2.copy()
            last_sim_parameters_filtered = sim_filtered.copy()

            

            last_sim_parameters_filtered["date"] = (
                last_sim_parameters_filtered["date"]
                .dt.tz_localize(None)
                .dt.strftime("%Y-%m-%d %H:%M")
            )

           

    zip_buffer.seek(0)

    st.download_button(
        "Download all files (ZIP)",
        data=zip_buffer.getvalue(),
        file_name=f"{base_name}.zip",
        mime="application/zip",
    )

    
    last_qid = sorted(hourly_all["query_id"].unique())[-1]
    preview_q = hourly_all[hourly_all["query_id"] == last_qid].copy()
    preview_q, _ = ensure_sorted_hourly(preview_q)
    preview_filtered = make_filtered_sorted(preview_q)

    
    st.subheader("Filtered preview (last query)")
    st.dataframe(
        raw_filtered.head(200), 
        use_container_width=True
    )


    st.subheader("Sim Parameters Preview (last query)")
    st.dataframe(
        last_sim_parameters.head(200),
        use_container_width=True
    )

    st.subheader("Sim Parameters Filtered Preview (last query)")
    st.dataframe(
        last_sim_parameters_filtered.head(200),
        use_container_width=True
    )


    # if "daily" in res and res["daily"] is not None and len(res["daily"]) > 0:
    #     st.subheader("Daily (preview)")
    #     st.dataframe(res["daily"], use_container_width=True)