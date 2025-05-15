import requests
import csv
import os
from datetime import datetime

# URL to crawl
station_ids = ["a541573213daa760b799",
            "d8466ee31278e426dbd8",
            "5949f20a303bcb0b4b081176",
            "5949f20a303bcb0b4b081177",
            "67f734ca76cfe716990c3514",
            "d01d6323f87da9a2a4b6"
            "cc1f1486b2113535bb1e",
            "67ca8ebd00c1ea609f6d8c1c",
            "89b85e7d6002954e0f42",
            "d2f6eded3f428aa9a7ae",
            "9c7b57505ca85fb23552",
            "714db8d74b1a20a6f242",
            "1a80166d2604bf3a9738",
            "0c9b4ab81d2d162834a4",
            "7298799d2147cbef007b",
            ]

for station_id in station_ids:
    url = f"https://website-api.airvisual.com/v1/stations/{station_id}?units.temperature=celsius&units.distance=kilometer&units.pressure=millibar&units.system=metric&AQI=US&language=vi"

    # Send GET request
    response = requests.get(url)
    data = response.json()


    # Extracting data
    current_time = datetime.now().replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    station_name = data.get("name")
    longitude = data.get("coordinates", {}).get("longitude")
    latitude = data.get("coordinates", {}).get("latitude")

    current = data.get("current", {})
    aqi = current.get("aqi")
    WHO_exposure = current.get("WHOExposure", {}).get("WHOExposure")

    # Extract pollutants
    pollutants = {p["pollutantName"]: p["concentration"] for p in current.get("pollutants", [])}
    pm25 = pollutants.get("pm25")
    pm10 = pollutants.get("pm10")
    o3 = pollutants.get("o3")
    no2 = pollutants.get("no2")
    so2 = pollutants.get("so2")
    co = pollutants.get("co")

    #Extract weather condition
    temperature = current.get("temperature")
    condition = current.get("condition")
    humidity = current.get("humidity")
    pressure = current.get("pressure")
    wind_speed = current.get("wind", {}).get("speed")
    wind_direction = current.get("wind", {}).get("direction")

    filename = "air_quality.csv"
    header = ["timestamp", "station_name", "longitude", "latitude", "aqi", "WHO_exposure",
            "PM2.5 (µg/m³)", "PM10 (µg/m³)", "O3 (µg/m³)", "NO2 (µg/m³)", "SO2 (µg/m³)", "CO (µg/m³)",
            "condition", "temperature (°)", "humidity (%)", "pressure", "wind_speed (km/h)", "wind_direction"]

    # Create CSV file with header if not exist
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(header)
        row = [current_time, station_name, longitude, latitude, aqi, WHO_exposure,
                pm25, pm10, o3, no2, so2, co,
                condition, temperature, humidity, pressure, wind_speed, wind_direction]
        writer.writerow(row)