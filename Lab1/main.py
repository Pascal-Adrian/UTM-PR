from functools import reduce

from Lab1.scrape import scrape_999_cars_product_page, scrape_999_cars_list_product_links
from models import CarModel, TotalPriceModel
from currency import get_bnm_currency_rate


def process_cars(cars: list[CarModel], price_low: float, price_high: float, convert_to_mdl: bool = True) -> TotalPriceModel:
    print("[info]: Processing car models ...")

    # convert the car prices to MDL
    rate = get_bnm_currency_rate('EUR')

    if rate is None:
        raise Exception('Failed to fetch the currency rate')  # raise exception if the rate is not found

    cars = list(
        map(lambda car: CarModel(car.manufacturer, car.model, car.price * rate, 'MDL', car.year, car.link), cars))

    # filter the cars by price
    cars = list(filter(lambda car: 200000 <= car.price <= 260000, cars))

    # calculate the total price
    total_price = reduce(lambda acc, car: acc + car.price, cars, 0.0)

    return TotalPriceModel(total_price, cars)


if __name__ == '__main__':
    link = scrape_999_cars_list_product_links(custom_request=True)
    cars = []
    for l in link:
        car = scrape_999_cars_product_page(l, custom_request=True)
        if car is not None:
            cars.append(car)
    cars_list = process_cars(cars, 200000, 260000, True)
    for car in cars_list.cars:
        print(car)
