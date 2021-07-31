from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_v1_router
from fastapi_framework import Config, ConfigField


class FastAPIConfig(Config):
    CONFIG_PATH = "config.yaml"
    CONFIG_TYPE = "yaml"

    name: str = ConfigField("FastAPI Project")
    version: str = ConfigField("0.1.0")


app = FastAPI(title=FastAPIConfig.name, version=FastAPIConfig.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/v1")
