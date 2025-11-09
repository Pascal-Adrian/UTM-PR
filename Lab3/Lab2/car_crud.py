from fastapi import UploadFile
from sqlalchemy.orm import Session
from Lab2.models import Car
from Lab2.schemas import CarCreate, Car as CarSchema
import json


async def get_car(db: Session, car_id: int) -> CarSchema:
    car = db.query(Car).filter(Car.id == car_id).first()
    return CarSchema(**car.__dict__)


async def get_cars(db: Session, skip: int = 0, limit: int = 10) -> list[CarSchema]:
    cars = db.query(Car).order_by(Car.id).offset(skip).limit(limit).all()
    return [CarSchema(**car.__dict__) for car in cars]


async def create_car(db: Session, car: CarCreate) -> CarSchema:
    db_car = Car(**car.dict())
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return CarSchema(**db_car.__dict__)


async def update_car(db: Session, car_id: int, car: CarCreate) -> CarSchema:
    db_car = db.query(Car).filter(Car.id == car_id).first()
    for key, value in car.dict().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return CarSchema(**db_car.__dict__)


async def delete_car(db: Session, car_id: int) -> CarSchema:
    db_car = db.query(Car).filter(Car.id == car_id).first()
    db.delete(db_car)
    db.commit()
    return CarSchema(**db_car.__dict__)


async def get_cars_from_json(db: Session, file: UploadFile) -> list[CarSchema]:
    cars = json.load(file.file)
    for car in cars:
        if len(car['link']) < 255:
            db_car = Car(**car)
            db.add(db_car)
    db.commit()
    cars = db.query(Car).where(Car.link.in_([car['link'] for car in cars])).all()
    return [CarSchema(**car.__dict__) for car in cars]
