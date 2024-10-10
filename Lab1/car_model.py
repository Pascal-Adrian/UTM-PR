class CarModel:
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
