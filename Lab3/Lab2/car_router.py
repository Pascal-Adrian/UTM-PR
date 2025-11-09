from fastapi import APIRouter, Depends, UploadFile
from Lab2.db import get_db
from Lab2.schemas import CarCreate, Car
import Lab2.car_crud as car_crud

CarRouter = APIRouter(
    prefix="/car",
    tags=["car"]
)


@CarRouter.get("/{car_id}", response_model=Car)
async def get_car(car_id: int, db=Depends(get_db)):
    response = await car_crud.get_car(db=db, car_id=car_id)
    return response


@CarRouter.get("", response_model=list[Car])
async def get_cars(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    response = await car_crud.get_cars(db=db, skip=skip, limit=limit)
    return response


@CarRouter.post(path="", response_model=Car)
async def create_car(car: CarCreate, db=Depends(get_db)):
    response = await car_crud.create_car(db=db, car=car)
    return response


@CarRouter.put("/{car_id}", response_model=Car)
async def update_car(car_id: int, car: CarCreate, db=Depends(get_db)):
    response = await car_crud.update_car(db=db, car_id=car_id, car=car)
    return response


@CarRouter.delete("/{car_id}", response_model=Car)
async def delete_car(car_id: int, db=Depends(get_db)):
    response = await car_crud.delete_car(db=db, car_id=car_id)
    return response


@CarRouter.post("/json")
async def get_cars_from_json(file: UploadFile, db=Depends(get_db)):
    response = await car_crud.get_cars_from_json(db=db, file=file)
    return response
