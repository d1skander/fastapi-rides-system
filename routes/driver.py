from fastapi import APIRouter, Depends
from routes.client import oauth2_sheme
from typing import Annotated


router = APIRouter(prefix="/driver",
                   tags=["drivers"])


'''@router.get("/news")
def app_news(log: Annotated[])'''