import json

import pika

from Lab1.models import CarModel
from Lab1.scrape import scrape_999_cars_list_product_links, scrape_999_cars_product_page
from Lab1.utils import serialize, save_to_file, process_cars

class Scrapper:
    def __init__(self, rabbitmq_host: str, credentials: pika.PlainCredentials = None):
        self.rabbitmq_host = rabbitmq_host
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host, credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='cars')
        self.cars = []

    def scrape(self):
        link = scrape_999_cars_list_product_links()
        for l in link:
            car = scrape_999_cars_product_page(l)
            if car is not None and len(car.link) < 255:
                self.enqueue(car)
                self.cars.append(car)

        cars_list = process_cars(self.cars, 200000, 260000, True)



    def enqueue(self, car: CarModel):
        self.channel.basic_publish(exchange='', routing_key='cars', body=json.dumps(car.__dict__))
        print(f'Scrapper: Car {car.manufacturer} {car.model} enqueued to rabbitmq.')

    def close(self):
        self.connection.close()



if __name__ == '__main__':
    scrapper = Scrapper('localhost', pika.PlainCredentials('admin', 'admin'))
    scrapper.scrape()
    scrapper.close()





