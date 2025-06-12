from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from services.pdf import process_file
import os

router = APIRouter()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Add OpenAPI security scheme
router.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": True
}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != os.getenv("LOAD_API_KEY"):
        raise HTTPException(
            status_code=403, detail="Invalid API Key"
        )
    return api_key_header

@router.post("/load")
async def load(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    await process_file(file)
    return {'message': 'File loaded successfully'}