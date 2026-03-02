import pandas as pd


def hourly_to_df(response, hourly_vars: list[str], time_col="time") -> pd.DataFrame:
    hourly = response.Hourly()
    times = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )
    df = pd.DataFrame({time_col: times})

    n = hourly.VariablesLength()
    if len(hourly_vars) > n:
        raise ValueError(f"Requested {len(hourly_vars)} hourly vars, but API returned {n}.")

    for i, var in enumerate(hourly_vars):
        df[var] = hourly.Variables(i).ValuesAsNumpy()
    return df



def daily_to_df(response, daily_vars: list[str], time_col="date") -> pd.DataFrame:
    daily = response.Daily()
    dates = pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=daily.Interval()),
        inclusive="left",
    )
    df = pd.DataFrame({time_col: dates})

    n = daily.VariablesLength()
    if len(daily_vars) > n:
        raise ValueError(f"Requested {len(daily_vars)} daily vars, but API returned {n}.")
    
    for i, var in enumerate(daily_vars):
        df[var] = daily.Variables(i).ValuesAsNumpy()
    return df