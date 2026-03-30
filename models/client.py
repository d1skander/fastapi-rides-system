from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator
from typing_extensions import Self
from fastapi import HTTPException


class UserBase(SQLModel):
    name: str = Field(min_length=3, max_length=30)
    surname: str = Field(min_length=3, max_length=30)
    residence: str | None = Field(default="Не указано", min_length=3, max_length=40)


class UserModel(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    phone: str
    password: str = Field(min_length=8, max_length=20)
    password_repeat: str = Field(min_length=8, max_length=20)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password_repeat:
            raise HTTPException(status_code=400, detail="Пароли должны совпадать")
        return self


    @field_validator("phone")
    @classmethod
    def number_verification(cls, value: str) -> str:
        if value.startswith("+") or value.startswith("7") or value.startswith("8"):
            value = value.replace(" ", "")
            if value.startswith("+"):
                value = value.replace("+", "", 1)
            if value.startswith("+"):
                value = "8" + value[1:]
        return value
    

class UserRead(UserBase):
    name: str = Field(min_length=3, max_length=30)
    surname: str = Field(min_length=3, max_length=30)
    residence: str | None = Field(default="Не указано", min_length=3, max_length=40)