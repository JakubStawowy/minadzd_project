from bs4 import BeautifulSoup
from requests import get
import pymongo

connection = pymongo.MongoClient(
    'localhost',
    27017
)

BASE_URL = 'https://bonito.pl'
BASE_PAGE_URL = 'https://bonito.pl/kategoria/muzyka/?page=<page_number>'


def extract_max_page(page_info):
    return page_info.split('z')[1].strip()


start_page = get(BASE_PAGE_URL.replace('<page_number>', '1'))
bs = BeautifulSoup(start_page.content, 'html.parser')

page_numbering_info = bs.find_all('img', class_='arrow_pagination')[0]\
    .parent.parent.find('div', class_='H4L').get_text()

# max_page_number = extract_max_page(page_numbering_info)
max_page_number = 10

db = connection.get_database('minadzd')
collection = db.get_collection('bonito_albums')

for page_number in range(int(max_page_number)):
    page = get(BASE_PAGE_URL.replace('<page_number>', str(page_number)))
    page_bs = BeautifulSoup(page.content, 'html.parser')

    for record in page_bs.find_all('div', class_='product_box'):
        title = record.find_next('a', title='Pokaż produkt').get_text()
        price = record.find_next('span', class_='H3B').get_text()
        sells_amount = record.find_next('b').get_text()

        collection.insert_one({'title': title, 'price': price, 'sells_amout': sells_amount})


