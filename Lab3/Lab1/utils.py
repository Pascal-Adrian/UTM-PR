from functools import reduce

from Lab1.scrape import scrape_999_cars_product_page, scrape_999_cars_list_product_links
from Lab1.models import CarModel, TotalPriceModel
from Lab1.currency import get_bnm_currency_rate


def process_cars(cars: list[CarModel], price_low: float, price_high: float, convert_to_mdl: bool = True) -> TotalPriceModel:
    print("[info]: Processing car models ...")

    # convert the car prices to MDL
    rate = get_bnm_currency_rate('EUR')

    if rate is None:
        raise Exception('Failed to fetch the currency rate')  # raise exception if the rate is not found

    if convert_to_mdl:
        cars = list(
            map(lambda car: CarModel(car.manufacturer, car.model, car.price * rate, 'MDL', car.year, car.link), cars))

    # filter the cars by price
    cars = list(filter(lambda car: price_low <= car.price <= price_high, cars))

    # calculate the total price
    total_price = reduce(lambda acc, car: acc + car.price, cars, 0.0)

    print("[info]: Successfully processed car models and created the total price model")

    return TotalPriceModel(total_price, cars)


def save_to_file(string: str, file_name: str, extension: str):
    print(f"[info]: Saving to file {file_name}.{extension} ...")

    with open(f'{file_name}.{extension}', 'w') as file:
        if extension == 'xml':
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(string)

    print(f"[info]: Successfully saved to file {file_name}.{extension}")


def serialize(cars_list: TotalPriceModel, extension: str, file_name: str = 'list'):
    if extension == 'json':
        save_to_file(cars_list.to_json(), file_name, 'json')
    elif extension == 'xml':
        save_to_file(cars_list.to_xml(), file_name, 'xml')
    else:
        raise Exception('Invalid extension')  # raise exception if the extension is invalid


if __name__ == '__main__':
    link = scrape_999_cars_list_product_links(custom_request=True)
    cars = []
    for l in link:
        car = scrape_999_cars_product_page(l, custom_request=True)
        if car is not None:
            cars.append(car)
    cars_list = process_cars(cars, 200000, 260000, True)

    serialize(cars_list, 'json', 'cars_list')
    serialize(cars_list, 'xml', 'cars_list')
