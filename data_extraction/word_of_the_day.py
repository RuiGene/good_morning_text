import requests
from bs4 import BeautifulSoup

url = 'https://www.dictionary.com/e/word-of-the-day/'

def get_word_of_the_day(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    word = soup.find('div', class_ = 'otd-item-headword__word').text

    definition_block = soup.find('div', class_ = 'otd-item-headword__pos')
    # Extract definition and not word type
    definition = definition_block.find_all('p')[1].text.strip()

    return word, definition

word, defintion = get_word_of_the_day(url)