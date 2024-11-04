import os
from dotenv import find_dotenv, load_dotenv
import requests

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
# DISTANCE_KEY = os.getenv("DISTANCE_KEY")
# DISTANCE_ID = os.getenv("DISTANCE_ID")

# url = "https://api.traveltimeapp.com/v4/time-filter"

# params = {
#     'type': 'driving',
#     "arrival_time": "2024-11-04T07:00:00Z",
#     "search_lat": 51.41070,
#     "search_lng": -0.15540,
#     "locations": "51.45974_-0.16531",
#     "app_id": DISTANCE_ID,
#     "api_key": DISTANCE_KEY
# }

# response = requests.get(url, params = params)

# if response.status_code == 200:
#     data = response.json()
# else:
#     print("error")

GOOGLE_KEY = os.getenv("GOOGLE_KEY")
home_address = os.getenv("home_address")

url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

origin = home_address
destination = '-36.85581, 174.76637'

params = {
    'origins': origin,
    'destinations': destination,
    'departure_time': 'now',
    'mode': 'driving',
    'key': GOOGLE_KEY
}

response = requests.get(url, params = params)

data = response.json()

travel_time_seconds = data["rows"][0]["elements"][0]["duration_in_traffic"]["value"]
travel_time_seconds