from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from json import load

with open('Lab2/config.json', 'r') as f:
    config = load(f)['db']


engine = create_engine(f'postgresql+psycopg2://{config["username"]}:{config["password"]}@{config["url"]}')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    metadata = MetaData()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
