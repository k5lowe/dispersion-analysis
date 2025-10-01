import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from date_range import past_date_input

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below

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
# len_date_ranges = len(date_ranges)
# # print(len_date_ranges)
for i in date_ranges:
	start_date = i[0]
	end_date = i[1]

	url = "https://api.open-meteo.com/v1/forecast"
	# url = "https://historical-forecast-api.open-meteo.com/v1/forecast"


	params = {
		"latitude": latitude,
		"longitude": longitude,
		"daily": "wind_gusts_10m_mean",
		"hourly": ["temperature_2m", "wind_speed_1000hPa", "wind_speed_975hPa", "wind_speed_950hPa", "wind_speed_925hPa", "wind_speed_900hPa", "wind_speed_850hPa", "wind_speed_800hPa", "wind_speed_700hPa", "wind_speed_600hPa", "wind_speed_500hPa", "wind_speed_400hPa", "wind_speed_300hPa", "wind_speed_250hPa", "wind_speed_200hPa", "wind_speed_150hPa", "wind_speed_70hPa", "wind_speed_100hPa", "wind_speed_50hPa", "wind_speed_30hPa", "wind_direction_1000hPa", "wind_direction_975hPa", "wind_direction_950hPa", "wind_direction_925hPa", "wind_direction_900hPa", "wind_direction_850hPa", "wind_direction_700hPa", "wind_direction_800hPa", "wind_direction_600hPa", "wind_direction_500hPa", "wind_direction_400hPa", "wind_direction_300hPa", "wind_direction_250hPa", "wind_direction_200hPa", "wind_direction_150hPa", "wind_direction_100hPa", "wind_direction_70hPa", "wind_direction_50hPa", "wind_direction_30hPa", "pressure_msl", "surface_pressure", "cloud_cover_high", "cloud_cover_mid", "cloud_cover_low", "is_day"],
		"models": "best_match",
		"wind_speed_unit": "kn",
		"start_date": start_date,
		"end_date": end_date,
	}



	responses = openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")


	hourly = response.Hourly()
	hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
	hourly_wind_speed_1000hPa = hourly.Variables(1).ValuesAsNumpy()
	hourly_wind_speed_975hPa = hourly.Variables(2).ValuesAsNumpy()
	hourly_wind_speed_950hPa = hourly.Variables(3).ValuesAsNumpy()
	hourly_wind_speed_925hPa = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_speed_900hPa = hourly.Variables(5).ValuesAsNumpy()
	hourly_wind_speed_850hPa = hourly.Variables(6).ValuesAsNumpy()
	hourly_wind_speed_800hPa = hourly.Variables(7).ValuesAsNumpy()
	hourly_wind_speed_700hPa = hourly.Variables(8).ValuesAsNumpy()
	hourly_wind_speed_600hPa = hourly.Variables(9).ValuesAsNumpy()
	hourly_wind_speed_500hPa = hourly.Variables(10).ValuesAsNumpy()
	hourly_wind_speed_400hPa = hourly.Variables(11).ValuesAsNumpy()
	hourly_wind_speed_300hPa = hourly.Variables(12).ValuesAsNumpy()
	hourly_wind_speed_250hPa = hourly.Variables(13).ValuesAsNumpy()
	hourly_wind_speed_200hPa = hourly.Variables(14).ValuesAsNumpy()
	hourly_wind_speed_150hPa = hourly.Variables(15).ValuesAsNumpy()
	hourly_wind_speed_70hPa = hourly.Variables(16).ValuesAsNumpy()
	hourly_wind_speed_100hPa = hourly.Variables(17).ValuesAsNumpy()
	hourly_wind_speed_50hPa = hourly.Variables(18).ValuesAsNumpy()
	hourly_wind_speed_30hPa = hourly.Variables(19).ValuesAsNumpy()
	hourly_wind_direction_1000hPa = hourly.Variables(20).ValuesAsNumpy()
	hourly_wind_direction_975hPa = hourly.Variables(21).ValuesAsNumpy()
	hourly_wind_direction_950hPa = hourly.Variables(22).ValuesAsNumpy()
	hourly_wind_direction_925hPa = hourly.Variables(23).ValuesAsNumpy()
	hourly_wind_direction_900hPa = hourly.Variables(24).ValuesAsNumpy()
	hourly_wind_direction_850hPa = hourly.Variables(25).ValuesAsNumpy()
	hourly_wind_direction_700hPa = hourly.Variables(26).ValuesAsNumpy()
	hourly_wind_direction_800hPa = hourly.Variables(27).ValuesAsNumpy()
	hourly_wind_direction_600hPa = hourly.Variables(28).ValuesAsNumpy()
	hourly_wind_direction_500hPa = hourly.Variables(29).ValuesAsNumpy()
	hourly_wind_direction_400hPa = hourly.Variables(30).ValuesAsNumpy()
	hourly_wind_direction_300hPa = hourly.Variables(31).ValuesAsNumpy()
	hourly_wind_direction_250hPa = hourly.Variables(32).ValuesAsNumpy()
	hourly_wind_direction_200hPa = hourly.Variables(33).ValuesAsNumpy()
	hourly_wind_direction_150hPa = hourly.Variables(34).ValuesAsNumpy()
	hourly_wind_direction_100hPa = hourly.Variables(35).ValuesAsNumpy()
	hourly_wind_direction_70hPa = hourly.Variables(36).ValuesAsNumpy()
	hourly_wind_direction_50hPa = hourly.Variables(37).ValuesAsNumpy()
	hourly_wind_direction_30hPa = hourly.Variables(38).ValuesAsNumpy()
	hourly_pressure_msl = hourly.Variables(39).ValuesAsNumpy()
	hourly_surface_pressure = hourly.Variables(40).ValuesAsNumpy()
	hourly_cloud_cover_high = hourly.Variables(41).ValuesAsNumpy()
	hourly_cloud_cover_mid = hourly.Variables(42).ValuesAsNumpy()
	hourly_cloud_cover_low = hourly.Variables(43).ValuesAsNumpy()
	hourly_is_day = hourly.Variables(44).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["temperature_2m"] = hourly_temperature_2m
	hourly_data["wind_speed_30hPa"] = hourly_wind_speed_30hPa
	hourly_data["wind_speed_50hPa"] = hourly_wind_speed_50hPa
	hourly_data["wind_speed_70hPa"] = hourly_wind_speed_70hPa
	hourly_data["wind_speed_100hPa"] = hourly_wind_speed_100hPa
	hourly_data["wind_speed_150hPa"] = hourly_wind_speed_150hPa
	hourly_data["wind_speed_200hPa"] = hourly_wind_speed_200hPa
	hourly_data["wind_speed_250hPa"] = hourly_wind_speed_250hPa
	hourly_data["wind_speed_300hPa"] = hourly_wind_speed_300hPa
	hourly_data["wind_speed_400hPa"] = hourly_wind_speed_400hPa
	hourly_data["wind_speed_500hPa"] = hourly_wind_speed_500hPa
	hourly_data["wind_speed_600hPa"] = hourly_wind_speed_600hPa
	hourly_data["wind_speed_700hPa"] = hourly_wind_speed_700hPa
	hourly_data["wind_speed_800hPa"] = hourly_wind_speed_800hPa
	hourly_data["wind_speed_850hPa"] = hourly_wind_speed_850hPa
	hourly_data["wind_speed_900hPa"] = hourly_wind_speed_900hPa
	hourly_data["wind_speed_925hPa"] = hourly_wind_speed_925hPa
	hourly_data["wind_speed_950hPa"] = hourly_wind_speed_950hPa
	hourly_data["wind_speed_975hPa"] = hourly_wind_speed_975hPa
	hourly_data["wind_speed_1000hPa"] = hourly_wind_speed_1000hPa
	hourly_data["wind_direction_30hPa"] = hourly_wind_direction_30hPa
	hourly_data["wind_direction_50hPa"] = hourly_wind_direction_50hPa
	hourly_data["wind_direction_70hPa"] = hourly_wind_direction_70hPa
	hourly_data["wind_direction_100hPa"] = hourly_wind_direction_100hPa
	hourly_data["wind_direction_150hPa"] = hourly_wind_direction_150hPa
	hourly_data["wind_direction_200hPa"] = hourly_wind_direction_200hPa
	hourly_data["wind_direction_250hPa"] = hourly_wind_direction_250hPa
	hourly_data["wind_direction_300hPa"] = hourly_wind_direction_300hPa
	hourly_data["wind_direction_400hPa"] = hourly_wind_direction_400hPa
	hourly_data["wind_direction_500hPa"] = hourly_wind_direction_500hPa
	hourly_data["wind_direction_600hPa"] = hourly_wind_direction_600hPa
	hourly_data["wind_direction_700hPa"] = hourly_wind_direction_700hPa
	hourly_data["wind_direction_800hPa"] = hourly_wind_direction_800hPa
	hourly_data["wind_direction_850hPa"] = hourly_wind_direction_850hPa
	hourly_data["wind_direction_900hPa"] = hourly_wind_direction_900hPa
	hourly_data["wind_direction_925hPa"] = hourly_wind_direction_925hPa
	hourly_data["wind_direction_950hPa"] = hourly_wind_direction_950hPa
	hourly_data["wind_direction_975hPa"] = hourly_wind_direction_975hPa
	hourly_data["wind_direction_1000hPa"] = hourly_wind_direction_1000hPa
	hourly_data["pressure_msl"] = hourly_pressure_msl
	hourly_data["surface_pressure"] = hourly_surface_pressure
	hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
	hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
	hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
	hourly_data["is_day"] = hourly_is_day

	hourly_dataframe = pd.DataFrame(data = hourly_data)

	start_time = pd.to_datetime("12:00:00").time()
	end_time   = pd.to_datetime("23:00:00").time()


	filtered_hourly_dataframe = hourly_dataframe[
		(hourly_dataframe['is_day']==1) & 
		(hourly_dataframe['cloud_cover_low']<=50) &
		(hourly_dataframe['date'].dt.time >= start_time) & 
		(hourly_dataframe['date'].dt.time <= end_time)]
	

	print("\nHourly data\n", filtered_hourly_dataframe)

	# # Process daily data. The order of variables needs to be the same as requested.
	# daily = response.Daily()
	# daily_wind_gusts_10m_mean = daily.Variables(0).ValuesAsNumpy()

	# daily_data = {"date": pd.date_range(
	# 	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	# 	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	# 	freq = pd.Timedelta(seconds = daily.Interval()),
	# 	inclusive = "left"
	# )}

	# daily_data["wind_gusts_10m_mean"] = daily_wind_gusts_10m_mean

	# daily_dataframe = pd.DataFrame(data = daily_data)
	# print("\nDaily data\n", daily_dataframe)

	user_file_name = input("Enter name of file you want to save as: ")
	if not user_file_name.lower().endswith(".csv"):
		user_file_name += ".csv"

	# Save DataFrame to CSV efficiently

	filtered_hourly_dataframe.to_csv(user_file_name, index=False)
	print(f"Daily data saved to {user_file_name}.csv")