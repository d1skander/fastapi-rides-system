from sqlmodel import SQLModel, Field, Column, JSON


class PathDeclaration(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    name_driver: str
    number_phone: str
    path_start: str
    path_end: str
    car: str
    number_of_passengers: int
    space_in_the_car: list[str] = Field(default=None, sa_column=Column(JSON))
    price: int