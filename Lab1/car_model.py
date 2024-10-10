class CarModel:
    def __init__(self, manufacturer, model, price, year, link):
        self.manufacturer = manufacturer
        self.model = model
        self.price = price
        self.year = year
        self.link = link

    def __str__(self):
        return (f'Model: {self.manufacturer} {self.model} \n'
                f'Year: {self.year} \n'
                f'Price: {self.price} € \n'
                f'URL: {self.link}\n')
