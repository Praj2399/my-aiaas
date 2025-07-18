from fastapi import APIRouter
from api.v1.endpoints import speech
from api.v1.auth import auth

api_router = APIRouter()
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"],responses={404: {"description": "Not found"}})
