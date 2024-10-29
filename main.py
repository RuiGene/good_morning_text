import smtplib
import os
from dotenv import find_dotenv, load_dotenv
from data_extraction.quote_of_the_day import getapi
from data_extraction.word_of_the_day import get_word_of_the_day
from data_extraction.weather import get_weather_data

# Getting relevant information
# Word of the day
word_url = 'https://www.dictionary.com/e/word-of-the-day/'
word, definition = get_word_of_the_day(word_url)

# Quote of the day
api_url = "https://zenquotes.io/api/random/"
quote, author = getapi(api_url)

# Weather
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
temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, graph = get_weather_data(url, params)


# Configuration
port = 587
smtp_server = "live.smtp.mailtrap.io"
login = "api"
sender = "testing@zr-yang.com"
receiver = "zrdanielyang@gmail.com"
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

Quote of the day: {quote} by {author}.

Word of the day: {word}. Definition: {definition}

"""

with smtplib.SMTP(smtp_server, port) as server:
    server.starttls()  # Secure the connection
    server.login(login, API_KEY)
    server.sendmail(sender, receiver, message)

print('Sent')