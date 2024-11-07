import smtplib
import os
import base64
import requests
import serpapi
from io import BytesIO
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

def get_quote(quote_url):
    response = requests.get(quote_url)
    data = response.json()

    if data:
        quote = data[0].get('q')
        author = data[0].get('a')
    
    return quote, author

def get_weather(weather_url, params):
    response = requests.get(weather_url, params = params)

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

        plt.close(fig)

        return(temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, fig)
        
    else:
        print("Error:", response.status_code, response.text)
        return None

def get_traffic(traffic_url, params):
    response = requests.get(traffic_url, params = params)
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

def get_news(params):
    result = serpapi.search(params)

    articles = [
        {
            "title": article["title"],
            "link": article["link"],
            "source": article["source"],
            "date": article["date"]
        }
        for article in result["news_results"]
    ]
    
    return articles

# Configuring data into HTML format
def get_base64_encoded_image(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return img_str

def generate_news_html(articles):
    news_items = ""
    
    for article in articles:
        title = article['title']
        link = article['link']
        date = article['date']
        news_items += f'<li><a href="{link}" target="_blank">{title}</a> ({date}) </li>\n'
        
    return news_items

def email(smtp_server, port, login, sender, receiver, key, html_message):
    today_date = datetime.now().strftime("%B %d")
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{today_date} Summary"
    message["To"] = receiver
    message["From"] = sender

    part = MIMEText(html_message, "html", "utf-8")
    message.attach(part)

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()  # Secure the connection
        server.login(login, key)
        server.sendmail(sender, receiver, message.as_string())

def main():
    dotenv_path = find_dotenv()
    load_dotenv(dotenv_path)

    # Retrieving data
    api_url = "https://zenquotes.io/api/random/"
    quote, author = get_quote(api_url)

    WEATHER_KEY = os.getenv("WEATHER_KEY")
    weather_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': WEATHER_KEY,
        'days': 1,
        'q': 'Auckland',
        'aqi': 'no',
        'alerts': 'no'
    }
    temp_c, wind_kph, humidity, feelslike_c, condition, icon_url, graph = get_weather(weather_url, params)

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
    traffic = get_traffic(traffic_url, params)

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
    articles = get_news(params)

    # Formatting data
    graph_base64 = get_base64_encoded_image(graph)

    traffic_list = ""
    for entry in traffic:
        destination = entry['destination_name']
        time_taken = entry['time_taken']
        traffic_list += f"<li>{destination}: {time_taken}</li>"

    news_html = generate_news_html(articles)

    # Message body
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

    key = os.getenv("API_KEY")

    email(
        smtp_server = "live.smtp.mailtrap.io",
        port = 587,
        login = 'api',
        sender = 'testing@zr-yang.com',
        receiver = 'zrdanielyang@gmail.com',
        key = key,
        html_message = html_message
    )

if __name__ == "__main__":
    main()