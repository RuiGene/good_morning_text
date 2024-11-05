import serpapi
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
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

def get_news_articles(params):

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

articles = get_news_articles(params)

print(articles)