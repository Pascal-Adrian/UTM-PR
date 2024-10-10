import json

import requests
from bs4 import BeautifulSoup


def scrape_999_cars_list_product_links(page: int = 1):
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


def main():
    links = scrape_999_cars_list_product_links()
    for link in links:
        print(link)


if __name__ == '__main__':
    main()
