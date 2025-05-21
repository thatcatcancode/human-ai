from fastapi import APIRouter, UploadFile, File
from services.pdf import process_file


router = APIRouter()

@router.post("/load")
async def load(file: UploadFile = File(...)):
    process_file(file)
    return {'message': 'File loaded successfully'}