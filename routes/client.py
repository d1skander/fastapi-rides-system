from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from models.client import UserModel
from models.model_base import SessionDep
from sqlmodel import Session, select


router = APIRouter(prefix="/client", tags=["client"],)


@router.post("/registration")
def registration_client(reg: UserModel,
                        session: SessionDep):
    reg.id = None
    session.add(reg)
    session.commit()
    return {"message": "Регистрация завершена"}


@router.post("/authentication")
def authentication_client():
    return {"message": "Успешный вход"}