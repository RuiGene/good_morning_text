import requests
import os
from dotenv import find_dotenv, load_dotenv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
WEATHER_KEY = os.getenv("WEATHER_KEY")

url = "http://api.weatherapi.com/v1/forecast.json"

params = {
    'key': WEATHER_KEY,
    'days': 1,
    'q': 'Auckland',
    'aqi': 'no',
    'alerts': 'no'
}

def get_weather_data(url, params):
    response = requests.get(url, params = params)

    if response.status_code == 200:
        data = response.json()

        # Extracting relevant data
        temp_c = data["current"]["temp_c"]
        wind_kph = data["current"]["wind_kph"]
        humidity = data["current"]["humidity"]
        feelslike_c = data["current"]["feelslike_c"]
        condition = data["current"]["condition"]["text"]
        icon_url = "https:" + data["current"]["condition"]["icon"]

        hours_data = data["forecast"]["forecastday"][0]["hour"]

        # Forecast from 8:00am to 10:00pm
        start_time = datetime.strptime(f"{data['forecast']['forecastday'][0]['date']} 08:00", "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(f"{data['forecast']['forecastday'][0]['date']} 22:00", "%Y-%m-%d %H:%M")

        # Extracting relevant forecasted data
        forecast_12h = [
            {
                "time": hour["time"],
                "temp_c": hour["temp_c"],
                "precip_mm": hour["precip_mm"],
                "chance_of_rain": hour["chance_of_rain"]
            }
            for hour in hours_data
            if start_time <= datetime.strptime(hour["time"], "%Y-%m-%d %H:%M") < end_time
        ]

        times = [entry["time"].split(" ")[1] for entry in forecast_12h]
        temperatures = [entry["temp_c"] for entry in forecast_12h]
        precipitations = [entry["precip_mm"] for entry in forecast_12h]

        # Initialising plot
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Temperature line graph
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Temperature (°C)", color='tab:orange')
        ax1.plot(times, temperatures, color = 'tab:orange', label = 'Temperature (°C)', marker = 'o')
        ax1.tick_params(axis = 'y', labelcolor = 'tab:orange')

        # Rainfall bar chart
        ax2 = ax1.twinx()
        ax2.set_ylabel("Rainfall (mm)", color = 'tab:blue')
        ax2.bar(times, precipitations, color = 'tab:blue', alpha = 0.6, label = 'Rainfall (mm)', width = 0.1)
        ax2.tick_params(axis = 'y', labelcolor = 'tab:blue')

        ax1.set_xticks(times)
        ax1.set_xticklabels(times, rotation = 45)

        plt.title("12 Hour Temperature and Rainfall Forecast")
        fig.tight_layout()

        return(temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, fig)
        
    else:
        print("Error:", response.status_code, response.text)
        return None

temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, graph = get_weather_data(url, params)