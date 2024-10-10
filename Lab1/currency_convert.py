import datetime

import requests
from bs4 import BeautifulSoup


def bnm_currency_converter(amount: float, currency: str, date: str = datetime.date.today().strftime('%d.%m.%Y')):
    url = f'https://www.bnm.md/ro/official_exchange_rates?get_xml=1&date={date}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'[error]: Failed to fetch page {url}')
        raise Exception(f'Failed to fetch page {url}')

    soup = BeautifulSoup(response.text, 'xml')

    rates = soup.find_all('Valute')

    rate_value = 0

    for rate in rates:
        if rate.find_next('CharCode').text == currency:
            rate_value = float(rate.find_next('Value').text.replace(',', '.'))

    if rate_value == 0:
        print(f'[error]: Currency not found in BNM data {url}')
        return None

    return amount * rate_value


