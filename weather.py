"""
This script defines an asynchronous function get_weather_forecast that fetches a 14-day weather
forecast for a city associated with a given event name (either "devconnect" or "breakpoint"). It
first uses the Open-Meteo geocoding API to obtain latitude and longitude coordinates for the
event's city, then retrieves forecast data—including daily maximum and minimum temperatures
and precipitation—using Open-Meteo’s weather API. The results are formatted into readable strings
and stored in an array, which is returned for later use. The file also includes configuration for
interacting with the ASI1 API, though it is not used within this function.
"""

import requests, os
import json
from dotenv import load_dotenv
import os

# Load environment variables from the .env file (if present)
load_dotenv()

ASI_1_API_KEY = os.getenv("ASI1_API_KEY")

asi1_api_key = ASI_1_API_KEY

ASI1_Endpoint = "https://api.asi1.ai/v1/chat/completions"


headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Authorization': f'Bearer {asi1_api_key}'  # agentverse api key; stored in agent secrets
}
array = []


async def get_weather_forecast(event):
    city = ""
    if event == "devconnect":
        city = "buenos aires"
    elif event == "breakpoint":
        city = "abu dhabi"
    # 1️⃣ Get city coordinates from Open-Meteo's geocoding API
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geocode_params = {"name": city, "count": 1}
    geo_response = requests.get(geocode_url, params=geocode_params)
    geo_data = geo_response.json()

    if "results" not in geo_data:
        print("City not found.")
        return

    latitude = geo_data["results"][0]["latitude"]
    longitude = geo_data["results"][0]["longitude"]
    location_name = geo_data["results"][0]["name"]

    # 2️⃣ Fetch 14-day weather forecast
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": 14,
        "timezone": "auto"
    }

    weather_response = requests.get(weather_url, params=weather_params)
    if weather_response.status_code != 200:
        print("Failed to fetch weather data.")
        return

    weather_data = weather_response.json()
    print(f"\n14-Day Weather Forecast for {location_name}:\n")

    # 3️⃣ Print daily forecast
    for i in range(len(weather_data["daily"]["time"])):
        date = weather_data["daily"]["time"][i]
        max_temp = weather_data["daily"]["temperature_2m_max"][i]
        min_temp = weather_data["daily"]["temperature_2m_min"][i]
        precipitation = weather_data["daily"]["precipitation_sum"][i]

        forecast = f"{date}: Max {max_temp}°C, Min {min_temp}°C, Precipitation {precipitation}mm"
        array.append(forecast)
    return array
