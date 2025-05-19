from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

# from routes import analyze
# from routes import rewrite
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",],  # Adjust to your frontend host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# app.include_router(analyze.router)
# app.include_router(rewrite.router)