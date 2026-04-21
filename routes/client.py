from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from models.client import UserModel
from models.model_base import SessionDep
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from models.token import create_access_token, get_current_active_user, Token
from datetime import timedelta
from geopy import Photon
from geopy.exc import GeocoderTimedOut
from geoalchemy2.shape import to_shape


import os
import bcrypt

load_dotenv()

router = APIRouter(prefix="/client", 
                   tags=["client"],)
geolocator = Photon(user_agent=os.getenv("USER_AGENT_GEO"), timeout=10000)


@router.post("/registration")
def registration_client(reg: UserModel,
                        session: SessionDep):
    reg.id = None
    username = select(UserModel).where(reg.username == UserModel.username)
    usernames = session.exec(username).all()
    if usernames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой пользователь уже существует")
    session.add(reg)
    session.commit()
    return {"message": "Регистрация завершена"}


@router.post("/authentication")
def authentication_client(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                          session: SessionDep):
    statement = select(UserModel).where(UserModel.username == form_data.username)
    result = session.exec(statement).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверное имя пользователя")
    if not bcrypt.checkpw(form_data.password.encode("utf-8"), result.password.encode("utf-8")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неправильный пароль")
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": result.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def get_me(current: Annotated[str, Depends(get_current_active_user)],
                 session: SessionDep):
    statement = select(UserModel).where(UserModel.username == current)
    result = session.exec(statement).first()
    data = []
    try:
        residence = to_shape(result.residence)
        residence_reverse = geolocator.reverse((residence.y, residence.x), timeout=30)
        str_residence = str(residence_reverse).split(",")
        item = {
            "username": result.username,
            "name": result.name,
            "surname": result.surname[0],
            "residence": str_residence[0]
        }
        data.append(item)
    except GeocoderTimedOut as err:
        raise err
    return data