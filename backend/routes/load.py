from fastapi import APIRouter, UploadFile, File
# from schemas import AnalyzePaperResponse
from services.pdf import process_file


router = APIRouter()

@router.post("/load")
async def load(file: UploadFile = File(...)):
    print('file', file)
    process_file(file)
    return {'message': 'File loaded successfully'}