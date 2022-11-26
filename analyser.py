import matplotlib.pyplot as plt
from pandas import DataFrame
from conf import get_local_db, get_cloud_db


def remove_album_duplicates(data):
    albums_cache = []
    result = []
    for album in data:
        if album['title'] not in albums_cache and album['artist'] != 'różni wykonawcy':
            albums_cache.append(album['title'])
            result.append(album)
    return result


def get_income(data, _type='artist'):
    income_dict = dict()
    for album in data:
        type_value = album[_type].lower()
        price = float(album['price'].split()[0].replace(',', '.')) * int(album['sells_amount'])
        if type_value in income_dict:
            income_dict[type_value] = income_dict[type_value] + price
        else:
            income_dict[type_value] = price
    return income_dict


def get_sells(data, _type='artist'):
    sells_dict = dict()
    for album in data:
        type_value = album[_type].lower()
        if type_value in sells_dict:
            sells_dict[type_value] = sells_dict[type_value] + int(album['sells_amount'])
        else:
            sells_dict[type_value] = int(album['sells_amount'])
    return sells_dict


def get_statistics(data):
    artist_income = get_income(data)
    artist_sells = get_sells(data)
    total_sum_of_artists_income = sum(artist_income.values())
    total_sum_of_artists_sells = sum(artist_sells.values())
    top_income_artist = max(artist_income, key=artist_income.get)
    top_sells_artist = max(artist_sells, key=artist_sells.get)

    label_income = get_income(data, _type='label')
    label_sells = get_sells(data, _type='label')
    total_sum_of_label_income = sum(label_income.values())
    total_sum_of_label_sells = sum(label_sells.values())
    top_income_label = max(label_income, key=label_income.get)
    top_sells_label = max(label_sells, key=label_sells.get)

    res = (artist_income.values(), artist_sells.values(), label_income.values(), label_sells.values())
    return res, DataFrame([
        [len(artist_sells), len(label_sells)],
        [total_sum_of_artists_income, total_sum_of_label_income],
        [top_income_artist, top_income_label],
        [artist_income[top_income_artist], label_income[top_income_label]],
        [total_sum_of_artists_sells, total_sum_of_label_sells],
        [top_sells_artist, top_sells_label],
        [artist_sells[top_sells_artist], label_sells[top_sells_label]]
    ], columns=['Artysta', 'Wytwórnia'], index=['Całkowita ilość',
                                                'Całkowita kwota sprzedaży',
                                                'Największą kwotę wygenerował',
                                                'Największa kwota sprzedaży',
                                                'Całkowita ilość sprzedanych albumów',
                                                'Najwięcej albumów sprzedał',
                                                'Największa ilość sprzedanych albumów'])


def plot_histogram(data, title):
    plt.rcParams["figure.figsize"] = (15, 15)
    plt.hist(data, bins=100, facecolor='g', log=True)
    plt.title(title)
    plt.grid(True)
    plt.show()


def plot_boxplot(data, title):
    plt.rcParams["figure.figsize"] = (10, 10)
    plt.boxplot(data)
    plt.title(title)
    plt.show()


# client, db = get_local_db()
client, db = get_cloud_db()

bonito_albums = db.bonito_albums
data_without_duplicates = remove_album_duplicates(bonito_albums.find())

client.close()

# Statistics
statistics_data, statistics = get_statistics(data_without_duplicates)
print(statistics)
statistics.head(n=len(statistics))

prices = [float(i["price"].split()[0].replace(",", ".")) for i in data_without_duplicates]
sells_amount = [int(i["sells_amount"]) for i in data_without_duplicates]

#Histogramy
plot_histogram(prices, 'Histogram of prices')
plot_histogram(sells_amount, 'Histogram of sells_amount')
plot_histogram(statistics_data[0], 'Histogram of artists incomes')
plot_histogram(statistics_data[1], 'Histogram of artists sells')
plot_histogram(statistics_data[2], 'Histogram of label incomes')
plot_histogram(statistics_data[3], 'Histogram of label sells')

# Boxploty
plot_boxplot(prices, 'Prices')
plot_boxplot(sells_amount, 'Sells_amount')
plot_boxplot(statistics_data[0], 'Artists incomes')
plot_boxplot(statistics_data[1], 'Artists sells')
plot_boxplot(statistics_data[2], 'Label incomes')
plot_boxplot(statistics_data[3], 'Label sells')
