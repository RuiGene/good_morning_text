import os
from dotenv import find_dotenv, load_dotenv
import requests

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
GOOGLE_KEY = os.getenv("GOOGLE_KEY")
home_address = os.getenv("home_address")

url = 'https://maps.googleapis.com/maps/api/distancematrix/json'

origin = home_address
destination = [
    '-36.85581, 174.76637', # University Address
    '-36.84801, 174.7578' # Work Address
]
destination_str = '|'.join(destination)

params = {
    'origins': origin,
    'destinations': destination_str,
    'departure_time': 'now',
    'mode': 'driving',
    'key': GOOGLE_KEY
}

def get_traffic_data(url, params):
    response = requests.get(url, params = params)

    results = []

    data = response.json()

    for i, element in enumerate(data["rows"][0]["elements"]):
        try:
            travel_time = element["duration_in_traffic"]["text"]
            
            destination_info = {
                'destination_name': data['destination_addresses'][i],
                'time_taken': travel_time
            }
            results.append(destination_info)
            
        except KeyError:
            return None
        
    return results