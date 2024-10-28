import requests

# API URL
api_url = "https://zenquotes.io/api/random/"

def getapi(url):
    response = requests.get(url)
    data = response.json()
    # print(data)

    if data:
        quote = data[0].get('q')
        author = data[0].get('a')
    
    # print(quote)
    # print(author)

    return quote, author

quote, author = getapi(api_url)
print(quote)
print(author)