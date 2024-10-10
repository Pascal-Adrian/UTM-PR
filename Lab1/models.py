from datetime import datetime

class CarModel:
    """
    Model for the car. Contains the manufacturer, model, price, currency, year and link.
    """

    def __init__(self, manufacturer: str, model: str, price: float, currency: str, year: int, link: str):
        self.manufacturer = manufacturer
        self.model = model
        self.price = price
        self.currency = currency
        self.year = year
        self.link = link

    def __str__(self):
        return (f'Model: {self.manufacturer} {self.model} \n'
                f'Year: {self.year} \n'
                f'Price: {self.price} {self.currency}\n'
                f'URL: {self.link}\n')


class TotalPriceModel:
    """
    Model for the total price of the cars. Contains the total price and the list of cars.
    """

    def __init__(self, total_price: float, cars: list[CarModel]):
        self.total_price = total_price
        self.cars = cars
        self.time_stamp = datetime.utcnow().timestamp()

    def __str__(self):
        return (f'Total price: {self.total_price}\n'
                f'Number of cars: {len(self.cars)}\n'
                f'Time stamp: {self.time_stamp}\n')
