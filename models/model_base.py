from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv


import os


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(DATABASE_URL, echo=True, plugins=["geoalchemy2"])


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def creade_db():
    SQLModel.metadata.create_all(engine)