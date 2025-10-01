import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from date_range import past_date_input

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)






default_launch_latitude = 47.965378
default_launch_longitude = -81.873536

def lat_coords_input():
	print("Latitude ∈ [-90,90]")
	while True:
	
		lat_input = input("Launch latitude (hit Enter for default):")
		try:
			if lat_input.strip() == "":
				print("Pressed enter. Using default value:", default_launch_latitude)
				lat_input = default_launch_latitude			
			
			elif -90 <= float(lat_input) <= 90:
				# print("User inputted latitude:", lat_input)
				lat_input = lat_input

				
			else:
				print("Invalid input: please enter numeric latitude coordinates.")
				continue


		except ValueError:
			print("Invalid input: please enter numeric latitude coordinates.")
			continue

		return lat_input
	
def lon_coords_input():
	print("Longitude ∈ [-180,180]")
	while True:
		lon_input = input("Launch latitude (hit enter for default):")
		try:
			if lon_input.strip() == "":
				print("Pressed enter. Using default value:", default_launch_longitude)
				lon_input = default_launch_longitude
			
			
			
			elif -180 <= float(lon_input) <= 180:
				# print("User inputted longitude:", lon_input)
				lon_input = lon_input

			else:
				print("Invalid input: please enter numeric longitude coordinates.")
				continue

		except ValueError:
			print("Invalid input: please enter numeric longitude coordinates.")
			continue

		return lon_input


latitude = lat_coords_input()
longitude = lon_coords_input()
date_ranges = past_date_input()


for i in date_ranges:
    start_date = i[0]
    end_date = i[1]
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "wind_gusts_10m_mean",
        "hourly": ["temperature_2m", "pressure_msl", "surface_pressure", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "wind_direction_100m_spread", "wind_direction_10m_spread", "wind_speed_100m_spread", "wind_speed_10m_spread", "is_day"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_pressure_msl = hourly.Variables(1).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(2).ValuesAsNumpy()
    hourly_cloud_cover_low = hourly.Variables(3).ValuesAsNumpy()
    hourly_cloud_cover_mid = hourly.Variables(4).ValuesAsNumpy()
    hourly_cloud_cover_high = hourly.Variables(5).ValuesAsNumpy()
    hourly_wind_direction_100m_spread = hourly.Variables(6).ValuesAsNumpy()
    hourly_wind_direction_10m_spread = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_speed_100m_spread = hourly.Variables(8).ValuesAsNumpy()
    hourly_wind_speed_10m_spread = hourly.Variables(9).ValuesAsNumpy()
    hourly_is_day = hourly.Variables(10).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["pressure_msl"] = hourly_pressure_msl
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
    hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
    hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
    hourly_data["wind_direction_100m_spread"] = hourly_wind_direction_100m_spread
    hourly_data["wind_direction_10m_spread"] = hourly_wind_direction_10m_spread
    hourly_data["wind_speed_100m_spread"] = hourly_wind_speed_100m_spread
    hourly_data["wind_speed_10m_spread"] = hourly_wind_speed_10m_spread
    hourly_data["is_day"] = hourly_is_day

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print("\nHourly data\n", hourly_dataframe)

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_wind_gusts_10m_mean = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}

    daily_data["wind_gusts_10m_mean"] = daily_wind_gusts_10m_mean

    daily_dataframe = pd.DataFrame(data = daily_data)
    print("\nDaily data\n", daily_dataframe)
	
    user_file_name = input("Enter name of file you want to save as: ")

    if not user_file_name.lower().endswith(".csv"):
       user_file_name += ".csv"

    daily_dataframe.to_csv(user_file_name, index=False)
    print(f"Daily data saved to {user_file_name}")
	