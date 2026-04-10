from pydantic import BaseModel
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.model_base import SessionDep
from models.client import UserModel
from sqlmodel import select


import jwt
import os


load_dotenv()


oauth2_sheme = OAuth2PasswordBearer(tokenUrl="/client/authentication")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("OAUTH_SECRET_KEY"), algorithm=os.getenv("OAUTH_ALGORITHM"))
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_sheme)], session: SessionDep):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Не удалось проверить учетные данные",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, os.getenv("OAUTH_SECRET_KEY"), algorithms=os.getenv("OAUTH_ALGORITHM"))
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = select(UserModel).where(token_data.username==UserModel.username)
    result = session.exec(user).first()
    if result is None:
        raise credentials_exception
    return result.username


async def get_current_active_user(current: Annotated[UserModel, Depends(get_current_user)]):
    if not current:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неактивный пользователь")
    return current