from fastapi import APIRouter, Depends
from sqlmodel import select
from models.token import oauth2_sheme, SessionDep, get_current_active_user
from typing import Annotated
from models.client import UserModel
from models.driver import PathDeclaration
from geopy.geocoders import Photon
from geoalchemy2.shape import to_shape, from_shape
from dotenv import load_dotenv


import os


load_dotenv()


router = APIRouter(prefix="/driver",
                   tags=["drivers"])
geolocator = Photon(user_agent=os.getenv("USER_AGENT_GEO"), timeout=10000)


@router.post("/announce")
def announce_a_trip(current: Annotated[str, Depends(get_current_active_user)],
                    path_model: PathDeclaration, session: SessionDep):
    path_model.id = None
    statement = select(UserModel).where(UserModel.username == current)
    user = session.exec(statement).first()
    path_model.name_driver = user.name + " " + user.surname[0] + "."
    path_model.number_phone = user.phone
    if path_model.path_start == "string":
        path_model.path_start = from_shape(to_shape(user.residence), srid=4326)
        session.add(path_model)
        session.commit()
        return {"message": "Обьявление вылажено", "начало": path_model.path_start}
    print(path_model.path_start)
    session.add(path_model)
    session.commit()
    return {"message": "Обьявление вылажено"}


@router.get("/get", response_model=PathDeclaration)
def get_announce(session: SessionDep):
    statement = select(PathDeclaration)
    results = session.exec(statement).all()
    return results