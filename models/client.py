from sqlmodel import SQLModel, Field
from pydantic import field_validator, model_validator, ConfigDict
from typing_extensions import Self, Any
import bcrypt


class UserBase(SQLModel):
    name: str = Field(min_length=3, max_length=30)
    surname: str = Field(min_length=3, max_length=30)
    residence: str | None = Field(default="Не указано", min_length=3, max_length=40)


class UserModel(UserBase, table=True):
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    username: str = Field(min_length=2, max_length=15)
    id: int | None = Field(default=None, primary_key=True)
    phone: str
    password: str = Field(min_length=8, max_length=100)
    password_repeat: str = Field(min_length=8, max_length=100, exclude=True)


    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password is None or self.password_repeat is None:
            return self
        if self.password.startswith("$2b$"):
            return self
        elif self.password != self.password_repeat:
            raise AttributeError("Пароли не совпадают")
        password_hash = bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt())
        self.password = password_hash.decode("utf-8")
        return self


    @field_validator("phone", mode="before")
    @classmethod
    def number_verification(cls, value: str) -> str:
        value = value.lstrip("+")
        value = value.strip()
        value = value.replace(" ", "")
        if value.isdigit() == False or len(value) != 11:
            raise ValueError("Неправильный ввод")
        if value[0] == "8":
            value = "7" + value[1:]
            print(value)
            return value
        elif value[0] == "7":
            print(value)
            return value
        
        else:
            raise ValueError("Неправильный ввод")
    

class UserRead(UserBase):
    name: str
    surname: str
    phone: str
    residence: str