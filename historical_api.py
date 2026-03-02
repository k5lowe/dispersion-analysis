# historical_api.py
from open_meteo_client import get_client
from open_meteo_parse import hourly_to_df, daily_to_df

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_historical(lat, lon, start_date, end_date, hourly_vars, daily_vars=None, extra_params=None):
    daily_vars = daily_vars or []
    extra_params = extra_params or {}

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": hourly_vars,
        "daily": daily_vars,
        "timezone": "auto",
        **extra_params,
    }

    openmeteo = get_client(expire_after=-1)  # cache forever like Open-Meteo example
    responses = openmeteo.weather_api(ARCHIVE_URL, params=params)
    r = responses[0]

    out = {}
    if hourly_vars:
        out["hourly"] = hourly_to_df(r, hourly_vars, time_col="time")
        out["hourly"]["source"] = "historical"
    if daily_vars:
        out["daily"] = daily_to_df(r, daily_vars, time_col="date")
        out["daily"]["source"] = "historical"
    return out