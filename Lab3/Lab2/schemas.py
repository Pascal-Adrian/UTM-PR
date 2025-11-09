from pydantic import BaseModel


class CarBase(BaseModel):
    manufacturer: str
    model: str
    price: float
    currency: str
    year: int
    link: str


class CarCreate(CarBase):
    pass


class Car(CarBase):
    id: int

    class Config:
        from_attributes: True


class Message(BaseModel):
    command: str
    message: str
