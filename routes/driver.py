from fastapi import APIRouter, Depends
from sqlmodel import select
from models.token import SessionDep, get_current_active_user
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


@router.get("/get", response_model=None)
def get_announce(session: SessionDep):
    statement = select(PathDeclaration)
    results = session.exec(statement).all()
    final_data = []
    for i in results:
        p_start = to_shape(i.path_start)
        p_end = to_shape(i.path_end)
        start_location = geolocator.reverse((p_start.y, p_start.x), timeout=30)
        end_location = geolocator.reverse((p_end.y, p_end.x), timeout=30)
        address_start = str(start_location.address)
        address_end = i.path_end = str(end_location.address)
        item = {
            "id": i.id,
            "name_driver": i.name_driver,
            "number_phone": i.number_phone,
            "car": i.car,
            "price": i.price,
            "number_of_passengers": i.number_of_passengers,
            "space_in_the_car": i.space_in_the_car,
            "path_start": address_start,
            "path_end": address_end
        }
        final_data.append(item)
    return final_data