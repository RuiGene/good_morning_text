import smtplib
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import find_dotenv, load_dotenv
from data_extraction.quote_of_the_day import getapi
from data_extraction.word_of_the_day import get_word_of_the_day
from data_extraction.weather import get_weather_data
from data_extraction.traffic import get_traffic_data
from data_extraction.news import get_news_articles

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
weather_url = "http://api.weatherapi.com/v1/forecast.json"
params = {
    'key': WEATHER_KEY,
    'days': 1,
    'q': 'Auckland',
    'aqi': 'no',
    'alerts': 'no'
}
temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, graph = get_weather_data(weather_url, params)

# Traffic
GOOGLE_KEY = os.getenv("GOOGLE_KEY")
home_address = os.getenv("home_address")
traffic_url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
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
traffic = get_traffic_data(traffic_url, params)

# News
NEWS_KEY = os.getenv("NEWS_KEY")
params = {
  "api_key": NEWS_KEY,
  "engine": "google",
  "q": "news",
  "location": "New Zealand",
  "google_domain": "google.co.nz",
  "gl": "nz",
  "hl": "en",
  "tbm": "nws",
  "num": "5"
}
articles = get_news_articles(params)

# Configuring data into HTML format
def get_base64_encoded_image(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return img_str
graph_base64 = get_base64_encoded_image(graph)

traffic_list = ""
for entry in traffic:
    destination = entry['destination_name']
    time_taken = entry['time_taken']
    traffic_list += f"<li>{destination}: {time_taken}</li>"

def generate_news_html(articles):
    news_items = ""
    
    for article in articles:
        title = article['title']
        link = article['link']
        date = article['date']
        
        news_items += f'<li><a href="{link}" target="_blank">{title}</a> ({date}) </li>\n'
        
    return news_items
news_html = generate_news_html(articles)

# HTML script
html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #333333;
            margin: 0;
            padding: 0;
        }}
        .container {{
            padding: 20px;
        }}
        h2 {{
            color: #4CAF50;
        }}
        .quote, .word, .weather, .traffic, .news {{
            padding: 10px;
            margin-bottom: 20px;
            border-bottom: 1px solid #dddddd;
        }}
        .news-article {{
            margin-bottom: 10px;
        }}
        .weather-icon {{
            vertical-align: middle;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Daily Update</h2>
        
        <div class="quote">
            <h3>Quote of the Day</h3>
            <p>"{quote}" - <em>{author}</em></p>
        </div>
        
        <div class="word">
            <h3>Word of the Day</h3>
            <p><strong>{word}</strong>: {definition}</p>
        </div>
        
        <div class="weather">
            <h3>Weather in Auckland</h3>
            <p><strong>Temperature:</strong> {temp_c}°C, feels like {feelslike_c}°C</p>
            <p><strong>Condition:</strong> {condition}</p>
            <img src="{icon_url}" alt="Weather Icon" class="weather-icon"/>
            <p><strong>Humidity:</strong> {humidity}%</p>
            <p><strong>Wind Speed:</strong> {wind_kph} km/h</p>
            <img src="data:image/png;base64,{graph_base64}" alt="Weather Graph" style="width:600px; height:auto;>
        </div>
        
        <div class="traffic">
            <h3>Traffic Updates</h3>
            <p>From home to:</p>
            <ul>
                {traffic_list}
            </ul>
        </div>
        
        <div class="news">
            <h3>Top News in New Zealand</h3>
            <ul>
                {news_html}
            </ul>
        </div>
    </div>
</body>
</html>
"""

# Configuration
port = 587
smtp_server = "live.smtp.mailtrap.io"
login = "api"
sender = "testing@zr-yang.com"
receiver = "zrdanielyang@gmail.com"
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")

today_date = datetime.now().strftime("%B %d")

message = MIMEMultipart("alternative")
message["Subject"] = f"{today_date} Summary"
message["To"] = receiver
message["From"] = sender

part = MIMEText(html_message, "html", "utf-8")
message.attach(part)

with smtplib.SMTP(smtp_server, port) as server:
    server.starttls()  # Secure the connection
    server.login(login, API_KEY)
    server.sendmail(sender, receiver, message.as_string())

print('Sent')