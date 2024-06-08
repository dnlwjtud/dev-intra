from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.dockers.api import router as dockers_api_router
from apps.dockers.view import router as dockers_view_router
from apps.view import router as global_view_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

app.include_router(global_view_router)
app.include_router(dockers_api_router, prefix="/api")
app.include_router(dockers_view_router, prefix="/dockers")
