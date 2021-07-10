from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import authentication, users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication)
app.include_router(users)
