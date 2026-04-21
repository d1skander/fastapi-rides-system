from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP
from typing import Any
from geoalchemy2 import Geometry
from pydantic import field_validator, ConfigDict
from geopy import Photon
from dotenv import load_dotenv
from typing import Any
from sqlmodel import SQLModel, Field, Column, JSON
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from pydantic import ConfigDict, field_validator
from geopy.geocoders import Photon
from geoalchemy2.elements import WKBElement
from datetime import datetime
import os


load_dotenv()


class PathDeclaration(SQLModel, table=True):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True, arbitrary_types_allowed=True)
    
    id: int | None = Field(primary_key=True, default=None)
    name_driver: str
    number_phone: str
    path_start: Any = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326)))
    path_end: Any = Field(sa_column=Column(Geometry(geometry_type="POINT", srid=4326)))
    car: str
    number_of_passengers: int
    space_in_the_car: list[str] = Field(default=None, sa_column=Column(JSON))
    price: int
    date_and_time: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))


    @field_validator("path_start", "path_end", mode="before")
    @classmethod
    def process_geometry(cls, value):
        if isinstance(value, WKBElement):
            return str(to_shape(value))


        if isinstance(value, str) and not value.startswith("POINT"):
            geolocator = Photon(user_agent=os.getenv("USER_AGENT_GEO"), timeout=30)
            location = geolocator.geocode(value, timeout=30)
            if location is None:
                raise ValueError(f"Не удалось найти координаты для адреса: {value}")
            return f"POINT({location.longitude} {location.latitude})"
        
        
        return value
    

class RouterSchema(SQLModel):
    start_route: str
    end_route: str