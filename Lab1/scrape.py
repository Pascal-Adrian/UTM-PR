import json
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from Lab1.models import CarModel


def scrape_999_cars_list_product_links(page: int = 1) -> List[str]:
    """
    Scrapes the 999.md website for car product links by page.
    :param page: int value of the page number to scrape; defaults to 1
    :return: list of strings containing the links to the car product pages
    """

    # getting the configuration from the config.json file
    with open('config.json', 'r') as file:
        config = json.load(file)

    # setting the arguments for the url of the request
    base_url = config['base_url']
    language = config['language']
    type = 'list'
    category = 'transport'
    sub_category = 'cars'

    # creating the url from the arguments
    url = f'{base_url}/{language}/{type}/{category}/{sub_category}?page={page}'

    print(f'[info]: Scraping the page {url} ...')

    # making the request to the url
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f'Failed to fetch page {url}')

    # parsing the response
    soup = BeautifulSoup(response.text, 'html.parser')

    # getting the list of cars from the page
    car_list = (soup.find_all('ul', class_='ads-list-photo large-photo')[0]
                .find_all_next('li', class_='ads-list-photo-item'))

    # extracting the links from the car list
    links = [base_url + car.find_next('a', class_='js-item-ad')['href'] for car in car_list]

    if links is None:
        raise Exception(f'Failed to extract links from page {url}')

    print(f'[info]: Successfully scraped {len(links)} links from the page {url}')

    return links


def scrape_999_cars_product_page(link: str) -> Optional[CarModel]:
    """
    Scrapes the 999.md car add pages for car data and returns a CarModel object.
    :param link: link to the 999.md car add page
    :return: CarModel object containing the car data
    """
    print(f'[info]: Scraping the page {link} ...')

    # making the request to the url
    response = requests.get(link)

    if response.status_code != 200:
        print(f'[error]: Failed to fetch page {link}')
        raise Exception(f'Failed to fetch page {link}')  # raise exception if the request failed

    # parsing the response
    soup = BeautifulSoup(response.text, 'html.parser')

    # extracting the price and currency
    price_data = soup.find_all('li', class_="adPage__content__price-feature__prices__price is-main")
    if len(price_data) == 0:
        print(f'[error]: Price not found on page {link}')
        return None
    price_data = price_data[0]
    price = (price_data.find_next('span', class_='adPage__content__price-feature__prices__price__value')
             .text.replace(' ', '').strip().replace(',', '.'))

    # check if the price is valid
    if price == '' or not price.isdigit():
        print(f'[error]: Price not found on page {link}')
        return None  # return None if the price is not valid

    currency = (price_data.find_next('span', class_='adPage__content__price-feature__prices__price__currency')
                .text.strip())

    # check if the currency is EUR
    if currency != '€':
        print(f'[error]: Currency is not EUR on page {link}')
        return None  # return None if the currency is not EUR

    # extracting the manufacturer and model
    features = soup.find_all('div', class_='adPage__content__features')[0].find_all('li')
    manufacturer = ''
    model = ''
    year = ''
    for feature in features:
        if 'Marc' in feature.text:
            manufacturer = feature.find(attrs={'itemprop': 'value'}).text.strip()
        if 'Model' in feature.text:
            model = feature.find(attrs={'itemprop': 'value'}).text.strip()
        if 'Anul fabrica' in feature.text:
            year = feature.find(attrs={'itemprop': 'value'}).text.strip()

    # check if the manufacturer and model are valid
    if model == '' or manufacturer == '':
        print(f'[error]: Manufacturer or model not found on page {link}')
        return None  # return None if the model or manufacturer is not valid

    # check if the year is valid
    if year == '' or not year.isdigit():
        print(f'[error]: Year not found on page {link}')
        return None

    return CarModel(manufacturer, model, float(price), 'EUR', year, link)
