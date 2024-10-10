from typing import Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def get_bnm_currency_rate(currency: str, date: str = datetime.today().strftime('%d.%m.%Y')) -> Optional[float]:
    """
    Fetches the currency rate from the BNM website for the given currency and date.

    :param currency: currency name abbreviation (e.g. 'USD', 'EUR')
    :param date: date string in the format 'dd.mm.yyyy' (e.g. '01.01.2021'); defaults to today's date
    :return: float value of the currency rate or None if the currency was not found
    """

    # fetch the xml data from the BNM website for the given date
    url = f'https://www.bnm.md/ro/official_exchange_rates?get_xml=1&date={date}'
    response = requests.get(url)

    # check if the request was successful
    if response.status_code != 200:
        print(f'[error]: Failed to fetch page {url}')
        raise Exception(f'Failed to fetch page {url}')

    soup = BeautifulSoup(response.text, 'xml')  # parse the xml data

    rates = soup.find_all('Valute')  # extract the rates from the xml data

    rate_value = 0.0  # default value for the rate

    # find the rate for the given currency
    for rate in rates:
        if rate.find_next('CharCode').text == currency:
            rate_value = float(rate.find_next('Value').text.replace(',', '.'))

    # return None if the currency was not found
    if rate_value == 0:
        print(f'[error]: Currency not found in BNM data {url}')
        return None

    return rate_value

