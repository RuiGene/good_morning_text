# Going to use wordnik
import requests
import os
from dotenv import find_dotenv, load_dotenv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
WORD_KEY = os.getenv("WORD_KEY")

def get_word_of_the_day(WORD_KEY):
    url = "https://api.wordnik.com/v4/words.json/wordOfTheDay"
    headers = {
        "api_key": WORD_KEY
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        word = data.get('word')
        definition = data['definitions'][0]['text'] if data.get('definitions') else "No definition available"
        return word, definition
    else:
        return None