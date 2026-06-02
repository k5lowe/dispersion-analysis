import config

hourly_vars = config.HOURLY_VARS

index1 = hourly_vars.index("temperature_2m")
index2 = hourly_vars.index("pressure_msl")
print(hourly_vars[0])
print("index1 is: ", index1)
print("index2 is: ", index2)
print(hourly_vars[index1])