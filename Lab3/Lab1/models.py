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

    def to_json(self):
        return str(self.__dict__).replace("'", '"')

    def to_xml(self):
        string = "<car>"
        for key, value in self.__dict__.items():
            string += f'<{key}>{value}</{key}>'
        return string + "</car>"


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

    def to_json(self):
        string = "{"
        for key, value in self.__dict__.items():
            if key == "cars":
                string += f'"{key}": ['
                for car in value:
                    string += car.to_json() + ", "
                string = string[:-2] + "], "
            else:
                string += f'"{key}": "{value}", '
        return string[:-2] + "}"

    def to_xml(self):
        string = "<total>"
        for key, value in self.__dict__.items():
            if key == "cars":
                string += "<cars>"
                for car in value:
                    string += car.to_xml()
                string += "</cars>"
            else:
                string += f'<{key}>{value}</{key}>'
        return string + "</total>"
