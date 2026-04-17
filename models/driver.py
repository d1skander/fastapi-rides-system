from sqlmodel import SQLModel, Field, Column, JSON
from typing import Any
from geoalchemy2 import Geometry
from pydantic import field_validator, ConfigDict
from geopy import Photon
from dotenv import load_dotenv


import os


load_dotenv()


class PathDeclaration(SQLModel, table=True):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: int | None = Field(primary_key=True, default=None)
    name_driver: str
    number_phone: str
    path_start: Any = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326)))
    path_end: Any = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326)))
    car: str
    number_of_passengers: int
    space_in_the_car: list[str] = Field(default=None, sa_column=Column(JSON))
    price: int


    @field_validator("path_end", mode="before")
    @classmethod
    def check_path_end(cls, value):
        geolocator = Photon(user_agent=os.getenv("USER_AGENT_GEO"), timeout=30)
        address = value
        location = geolocator.geocode(address, timeout=30)
        if value is None:
            raise AttributeError("Не удалось обнаружить координаты")
        value = f"POINT({location.longitude} {location.latitude})"
        return value