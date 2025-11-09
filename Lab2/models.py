from db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text


class Car(Base):
    __tablename__ = 'Cars'

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String(255), index=True, nullable=False)
    model = Column(String(255), index=True)
    price = Column(Float, index=True)
    currency = Column(String(10), index=True)
    year = Column(Integer, index=True)
    link = Column(String(255), index=True)

    def __repr__(self):
        return f'<Car {self.manufacturer} {self.model} {self.year}>'