from fastapi import APIRouter

router: APIRouter = APIRouter(
    prefix="/inspectors"
)

@router.get("/")
def test():
    pass

