from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routers import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=["*"],
    allow_methods=["POST"]
)
app.include_router(router , tags=["Upload_File"])