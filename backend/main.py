from fastapi import FastAPI
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv
load_dotenv()

from routes import load, chat

from fastapi.middleware.cors import CORSMiddleware

# Define security scheme
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

app = FastAPI(
    title="Human AI API",
    description="API for human-ai project",
    version="1.0.0",
    openapi_tags=[{"name": "load", "description": "Operations for loading documents"}],
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://thatcatcancode.github.io",], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root()
    return {"message": "Hello World"}

app.include_router(load.router)
app.include_router(chat.router)