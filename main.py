from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from inspector.app import ContainerManager

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    manager = ContainerManager()
    return templates.TemplateResponse(
        request=request, name="infra.html", context={"container_status": manager.get_container_status_list()}
    )

@app.get("/status")
async def get_container_status(request: Request):
    pass


