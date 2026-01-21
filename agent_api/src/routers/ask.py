from fastapi import APIRouter


router = APIRouter(
    tags=["ask"]
)

@router.get("/ask")
async def ask_question():
    return {"message": "This is the ask endpoint"}
