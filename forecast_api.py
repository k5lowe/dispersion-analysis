# forecast_api.py
from open_meteo_client import get_client
from open_meteo_parse import hourly_to_df, daily_to_df

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_forecast(lat, lon, start_date, end_date, hourly_vars, daily_vars=None, extra_params=None):
    daily_vars = daily_vars or []
    extra_params = extra_params or {}

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": hourly_vars,
        "timezone": "auto",
        **extra_params,
    }
    
    if daily_vars:
        params["daily"] = daily_vars

    openmeteo = get_client(expire_after=3600)
    responses = openmeteo.weather_api(FORECAST_URL, params=params)
    r = responses[0]

    out = {}
    if hourly_vars:
        out["hourly"] = hourly_to_df(r, hourly_vars, time_col="time")
        out["hourly"]["source"] = "forecast"
    if daily_vars:
        out["daily"] = daily_to_df(r, daily_vars, time_col="date")
        out["daily"]["source"] = "forecast"
    return out