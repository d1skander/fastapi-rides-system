from fastapi import FastAPI
from routes.client import router as client_router
from models.model_base import creade_db, engine
from admins.admin import setup_admin


import uvicorn


app = FastAPI()


setup_admin(app, engine)


app.include_router(client_router)


if __name__== "__main__":
    creade_db()
    config = uvicorn.Config("main:app", port=8787, log_level="info", reload=True)
    server = uvicorn.Server(config)
    server.run()