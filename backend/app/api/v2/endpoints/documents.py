from fastapi import APIRouter

router = APIRouter()

@router.get("/placeholder")
async def v2_documents_placeholder():
    return {"message": "V2 Documents Endpoint Placeholder"}
