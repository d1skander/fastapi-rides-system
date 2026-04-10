from sqladmin import ModelView, Admin
from models.client import UserModel as user
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from dotenv import load_dotenv


import os

load_dotenv()

def setup_admin(app, engine):
    class AuthAdmin(AuthenticationBackend):
        async def login(self, request: Request):
            form = await request.form()
            username, password = form["username"], form["password"]
            request.session.update({"username": username, "password": password})
            return True
        async def logout(self, request: Request):
            request.session.clear()
            return True
        async def authenticate(self, request: Request):
            username = request.session.get("username")
            password = request.session.get("password")
            admin_username = os.getenv("ADMIN_NAME")
            admin_password = os.getenv("ADMIN_PASSWORD")
            if username != admin_username and password != admin_password:
                return False
            return True


    class RiderAdmin(ModelView, model=user):
        column_list = [user.name, user.surname, user.residence,
                        user.phone, user.id,user.password, user.username]

    auth_back = AuthAdmin(secret_key=os.getenv("ADMIN_SECRET_KEY"))
    admin = Admin(app, engine, authentication_backend=auth_back)
    admin.add_view(RiderAdmin)