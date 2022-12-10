import os
from urllib.parse import urljoin

import requests
from fastapi import APIRouter, Response
from pydantic import BaseModel
from starlette.responses import JSONResponse

LEMMY_URL = os.environ["LEMMY_URL"]


class Register(BaseModel):
    username: str
    email: str
    password: str
    password_verify: str


class Login(BaseModel):
    username_or_email: str
    password: str


class BeginCurate(BaseModel):
    auth: str
    query: str
    original_urls: list[str]


def create_router() -> APIRouter:
    router = APIRouter(prefix="/user", tags=["user"])

    community_id = get_community_id()

    @router.post("/register")
    def user_register(register: Register) -> Response:
        lemmy_register = {
            "username": register.username,
            "email": register.email,
            "password": register.password,
            "password_verify": register.password_verify,
            "answer": None,
            "captcha_answer": None,
            "captcha_uuid": None,
            "honeypot": None,
            "show_nsfw": False,
        }
        request = requests.post(urljoin(LEMMY_URL, "api/v3/user/register"), json=lemmy_register)
        return Response(content=request.content, status_code=request.status_code, media_type="text/json")

    @router.post("/login")
    def user_login(login: Login) -> Response:
        request = requests.post(urljoin(LEMMY_URL, "api/v3/user/login"), json=login.dict())
        return Response(content=request.content, status_code=request.status_code, media_type="text/json")

    @router.post("/query/create")
    def user_begin_curate(begin_curate: BeginCurate):
        create_post = {
            "auth": begin_curate.auth,
            "body": None,
            "community_id": community_id,
            "honeypot": None,
            "language_id": None,
            "name": None,
            "nsfw": None,
            "url": None,
        }

    return router


def get_community_id() -> str:
    request = requests.get(urljoin(LEMMY_URL, "api/v3/community?name=main"))
    community = request.json()
    return community["community_view"]["community"]["id"]


