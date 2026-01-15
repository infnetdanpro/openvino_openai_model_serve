import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .views import router


def create_app():
    app = FastAPI(title="OpenVINO LLM API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)
    app.state.model_path = os.getenv("MODEL_PATH", "llm")
    app.state.available_models = [
        "gemma-3-4b-it-int4-cw-ov"
    ]  # TODO: get models from dir llm

    return app
