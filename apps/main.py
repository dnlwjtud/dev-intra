from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.inspector.api import router as inspector_api_router
from apps.view import router as view_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

app.include_router(view_router)
app.include_router(inspector_api_router, prefix="/api")
