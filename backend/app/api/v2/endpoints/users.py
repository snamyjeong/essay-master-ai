from fastapi import APIRouter

router = APIRouter()

@router.get("/placeholder")
async def v2_users_placeholder():
    return {"message": "V2 Users Endpoint Placeholder"}
