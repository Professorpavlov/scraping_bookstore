import json
import requests
from bs4 import BeautifulSoup
import datetime
import csv
import time


start_time = time.time()
def get_data():
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')

    with open(f'labirint_{cur_time}.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'Название книги',
                'Автор',
                'Издательство и серия',
                'Цена со скидкой',
                'Цена без скидки',
                'Процент от скидки',
                'Наличие'
            )
        )

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    url = 'https://www.labirint.ru/genres/2308/?available=1&price_min=&price_max=&form-pubhouse=&id_genre=2308&paperbooks=1#catalog-navigation'
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    page_count = int(soup.find('div', class_='pagination-number__right').find_all('a')[-1].text)

    for page in range(1, page_count + 1):
        url = f'https://www.labirint.ru/genres/2308/?order=date&way=back&form-pubhouse=&id_genre=2308&available=1&preorder=1&wait=1&price_min=&price_max=&page={page}'

        response_page = requests.get(url=url, headers=headers)
        soup_page = BeautifulSoup(response_page.text, 'lxml')

        books_data = []

        all_items = soup_page.find('div', class_='js-content-block-tab').find('div', class_='genres-carousel__container').find_all(class_='genres-carousel__item')
        for info in all_items:

            try:
                name = info.find('a', class_='product-title-link').get('title')
            except:
                name = 'Название книги отсутствует'

            try:
                new_price = info.find('span', class_='price-val').text.replace('₽', '').replace(' ', '').strip()
            except:
                new_price = 'Цена со скидкой отсутствует'

            try:
                old_price = info.find('span', class_='price-old').text.replace(' ', '').strip()
            except:
                old_price = 'Старая цена отсутствует'

            try:
                percent_discount = round(((int(old_price) - int(new_price)) / int(old_price)) * 100)
            except:
                percent_discount = 'Скидки нет - процента нет'


            try:
                author = info.find('div', class_='product-author').text.strip()
            except:
                author = 'Автор отсутствует'

            try:
                publishing = info.find('a', class_='product-pubhouse__pubhouse').text.strip()
                series = info.find(class_='product-pubhouse__series').text.strip()
                publishing = ':'.join([publishing, series])
            except:
                publishing = 'Издательство отсутствует'

            try:
                availability = info.find('div', class_='buy-avaliable').text.strip()
                if availability == 'В КОРЗИНУ':
                    availability = 'В наличии'
                elif availability == 'ПРЕДЗАКАЗ':
                    availability = 'Предзаказ'
                elif availability == 'ОЖИДАЕТСЯ':
                    availability = 'Ожидается '
            except:
                availability = 'В наличии отсутствует'

            books_data.append(
                {
                    'book_title': name,
                    'author': author,
                    'publisher_and_series': publishing,
                    'price_with_discount': new_price,
                    'price_without_discount': old_price,
                    'percentage_of_discount': percent_discount,
                    'availability': availability

                }
            )

            with open(f'labirint_{cur_time}.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        name,
                        author,
                        publishing,
                        new_price,
                        old_price,
                        percent_discount,
                        availability
                    )
                )

        print(f'Обработана {page}/{page_count}')
        time.sleep(1)

    with open(f'labirint_{cur_time}.json', 'w', encoding='utf-8') as json_file:
        json.dump(books_data, json_file, indent=4, ensure_ascii=False)




def main():
    get_data()
    finish_time = time.time() - start_time
    print(f'Затраченное на работу скрипта время: {finish_time}')

if __name__ == '__main__':
    main()
