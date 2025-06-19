from fastapi import FastAPI, Request
from fastapi.security.api_key import APIKeyHeader
from langsmith.middleware import TracingMiddleware
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import time
import os

load_dotenv()

from routes import load, chat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('app.log')  # File handler
    ]
)

logger = logging.getLogger(__name__)

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

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Log response details
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://thatcatcancode.github.io",], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TracingMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up...")
    # Log environment variables (without sensitive values)
    env_vars = {
        "PINECONE_API_KEY": "SET" if os.getenv("PINECONE_API_KEY") else "NOT SET",
        "PINECONE_INDEX_NAME": os.getenv("PINECONE_INDEX_NAME"),
        "GROQ_API_KEY": "SET" if os.getenv("GROQ_API_KEY") else "NOT SET"
    }
    logger.info(f"Environment variables: {env_vars}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down...")

app.include_router(load.router)
app.include_router(chat.router)