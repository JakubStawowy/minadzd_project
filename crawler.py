from bs4 import BeautifulSoup
from requests import get
from pymongo import MongoClient

from conf import get_secrets

secrets = get_secrets()
connection_local = MongoClient(
    'localhost',
    27017,
    username=secrets['local_db_user'],
    password=secrets['local_db_passwd'],
    authMechanism='SCRAM-SHA-256'
)

connection_cloud = MongoClient(f'mongodb+srv://'
                               f'{secrets["cloud_db_user"]}:{secrets["cloud_db_passwd"]}@projectminadzd.5zghkdq.mongodb.net/'
                               '?retryWrites=true&w=majority')


BASE_URL = 'https://bonito.pl'
BASE_PAGE_URL = 'https://bonito.pl/kategoria/muzyka/?page=<page_number>'


def extract_max_page(page_info):
    return page_info.split('z')[1].strip()


start_page = get(BASE_PAGE_URL.replace('<page_number>', '1'))
bs = BeautifulSoup(start_page.content, 'html.parser')

page_numbering_info = bs.find_all('img', class_='arrow_pagination')[0]\
    .parent.parent.find('div', class_='H4L').get_text()

max_page_number = extract_max_page(page_numbering_info)

db_local = connection_local.get_database('minadzd')
collection_local = db_local.get_collection('bonito_albums')

db_cloud = connection_cloud.get_database('MiNADZD')
collection_cloud = db_cloud.get_collection('bonito_albums')

for page_number in range(int(max_page_number)):
    page = get(BASE_PAGE_URL.replace('<page_number>', str(page_number)))
    page_bs = BeautifulSoup(page.content, 'html.parser')

    for record in page_bs.find_all('div', class_='product_box'):
        title_section = record.find_next('a', title='Pokaż produkt')
        title = title_section.get_text()
        price = record.find_next('span', class_='H3B').get_text()
        old_price_section = record.find_next('span', class_='T2L')
        if old_price_section is not None:
            old_price = old_price_section.get_text()
        else:
            old_price = ''

        sells_amount_section = record.find_next('b')
        if sells_amount_section is not None:
            sells_amount = sells_amount_section.get_text()
        else:
            sells_amount = '0'

        available_section = record.find_next('img', alt='Dostępny')
        if available_section is not None:
            available_amount = available_section.parent.find_all('span', class_='H4L')[1].get_text().split(' ')[0]
        else:
            available_amount = '0'

        artist_label = title_section.parent.find_all('div', class_='T2L')
        artist = artist_label[0].get_text()
        if len(artist_label) > 1:
            label = artist_label[1].get_text()
        else:
            label = ''

        document = {
            'title': title,
            'artist': artist,
            'label': label,
            'price': price,
            'old_price': old_price,
            'copies_available': available_amount,
            'sells_amount': sells_amount
        }

        collection_local.insert_one(document)
        collection_cloud.insert_one(document)


connection_local.close()
connection_cloud.close()
