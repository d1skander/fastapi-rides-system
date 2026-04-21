from fastapi import APIRouter, Depends
from sqlmodel import select
from models.token import SessionDep, get_current_active_user
from typing import Annotated
from models.client import UserModel
from models.driver import PathDeclaration
from geopy.geocoders import Photon
from geoalchemy2.shape import to_shape, from_shape
from dotenv import load_dotenv
from shapely.geometry import Point
from geopy import distance


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
    session.add(path_model)
    session.commit()
    return {"message": "Обьявление вылажено"}


@router.get("/get_all_announce")
def get_announce(session: SessionDep):
    statement = select(PathDeclaration)
    results = session.exec(statement).all()
    final_data = []
    for i in results:
        p_start = to_shape(i.path_start)
        p_end = to_shape(i.path_end)
        start_location = geolocator.reverse((p_start.y, p_start.x), timeout=30)
        end_location = geolocator.reverse((p_end.y, p_end.x), timeout=30)
        address_start = str(start_location.address).split(",")
        address_end = i.path_end = str(end_location.address).split(",")
        item = {
            "id": i.id,
            "name_driver": i.name_driver,
            "number_phone": i.number_phone,
            "car": i.car,
            "price": i.price,
            "number_of_passengers": i.number_of_passengers,
            "space_in_the_car": i.space_in_the_car,
            "path_start": address_start[0],
            "path_end": address_end[0],
            "date_and_time": i.date_and_time
        }
        final_data.append(item)
    return final_data


@router.get("/get_specific_route/{start_route}/{end_route}")
def specific_route(current: Annotated[str, Depends(get_current_active_user)],
                   session: SessionDep,
                   start_route: str, end_route: str):
    data = []
    if start_route == "None":
        statement = select(UserModel).where(UserModel.username == current)
        user = session.exec(statement).first()
        user_shape = to_shape(user.residence)
        location = geolocator.reverse((user_shape.y, user_shape.x), timeout=30)
        route = str(location).split(",")
        city = route[0]
        item = {
            "start_route": city,
            "end_route": end_route
        }
        data.append(item)
        return data
    elif start_route != "None":
        print("Условие началось")
        adrees = start_route
        print(f"adrees: {adrees}")
        location = geolocator.geocode(adrees, timeout=30)
        print(f"location {location}")
        shape_location = from_shape(Point(location.longitude, location.latitude), srid=4326)
        print(f"shape_location: {shape_location}")
        statement = select(PathDeclaration).where(PathDeclaration.path_start == shape_location)
        print(f"statement: {statement}, residence: {PathDeclaration.path_start}")
        route = session.exec(statement).all()
        print(f"route {route}")
        for i in route:
            print("Цикл начался")
            p_start = to_shape(i.path_start)
            p_end = to_shape(i.path_end)
            start_location = geolocator.reverse((p_start.y, p_start.x), timeout=30)
            end_location = geolocator.reverse((p_end.y, p_end.x), timeout=30)
            address_start = str(start_location.address).split(",")
            address_end = str(end_location.address).split(",")
            item = {
                "id": i.id,
                "name_driver": i.name_driver,
                "number_phone": i.number_phone,
                "car": i.car,
                "price": i.price,
                "number_of_passengers": i.number_of_passengers,
                "space_in_the_car": i.space_in_the_car,
                "path_start": address_start[0],
                "path_end": address_end[0],
                "date_and_time": i.date_and_time
            }
            print(item)
            data.append(item)
        return data
    return data


@router.get("/get_route/{start_route}/{end_route}")
def specific_route(current: Annotated[str, Depends(get_current_active_user)],
                   session: SessionDep,
                   start_route: str, end_route: str):
    data = []
    if start_route == "None":
        statement = select(UserModel).where(UserModel.username == current)
        user = session.exec(statement).first()
        user_shape = to_shape(user.residence)
        statement_path = select(PathDeclaration)
        path_result = session.exec(statement_path).all()
        for i in path_result:
            shape_path_start = to_shape(i.path_start)
            distance_user = (user_shape.y, user_shape.x)
            distance_announce = (shape_path_start.y, shape_path_start.x)
            final_distance = distance.distance(distance_user, distance_announce).km
            dict_distance = {
                "name": i.name_driver,
                "distance": final_distance
            }
            data.append(dict_distance)
    return data