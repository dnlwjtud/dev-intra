from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from apps.inspector.app import ContainerManager
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    manager = ContainerManager()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"container_status": manager.get_container_status_list()}
    )

