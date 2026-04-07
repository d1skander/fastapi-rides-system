from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator, ConfigDict
from typing_extensions import Self
from fastapi import HTTPException


class UserBase(SQLModel):
    name: str = Field(min_length=3, max_length=30)
    surname: str = Field(min_length=3, max_length=30)
    residence: str | None = Field(default="Не указано", min_length=3, max_length=40)


class UserModel(UserBase, table=True):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    id: int | None = Field(default=None, primary_key=True)
    phone: str
    password: str = Field(min_length=8, max_length=20)
    password_repeat: str = Field(min_length=8, max_length=20)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise HTTPException(status_code=400, detail="Пароли должны совпадать")
        return self


    @field_validator("phone", mode="before")
    @classmethod
    def number_verification(cls, value: str) -> str:
        print(f"Валидатор видит: {value}") 
        value = value.lstrip("+")
        value = value.strip()
        value = value.replace(" ", "")
        if value.isdigit() == False or len(value) != 11:
            raise HTTPException(status_code=400, detail="Неправильный ввод")
        if value[0] == "8":
            value = "7" + value[1:]
            print(value)
            return value
        elif value[0] == "7":
            print(value)
            return value
        
        else:
            raise HTTPException(status_code=400, detail="Неправильный ввод")
    

class UserRead(UserBase):
    name: str = Field(min_length=3, max_length=30)
    surname: str = Field(min_length=3, max_length=30)
    phone: str
    residence: str | None = Field(default="Не указано", min_length=3, max_length=40)